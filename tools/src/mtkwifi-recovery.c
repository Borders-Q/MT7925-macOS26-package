/* SPDX-License-Identifier: ISC
 * Minimal recovery-environment client for MtkWlan 0.12.1.
 * Uses the upstream public IOUserClient ABI and upstream WPA PMK derivation.
 * This is a userspace client, not a new kernel driver.
 * Copyright (c) 2026. Permission to use, copy, modify, and distribute this
 * software for any purpose with or without fee is hereby granted, provided
 * this notice appears in all copies. THE SOFTWARE IS PROVIDED "AS IS",
 * WITHOUT ANY WARRANTY. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "MtkUserApi.h"
#include "MtkCrypto.h"

_Static_assert(sizeof(struct mtk_join_params) == 76, "join ABI changed");
_Static_assert(sizeof(struct mtk_scan_result) == 52, "scan ABI changed");
_Static_assert(sizeof(struct mtk_status) == 128, "status ABI changed");

static int selftest(void) {
    static const uint8_t expected[32] = {
        0xf4,0x2c,0x6f,0xc5,0x2d,0xf0,0xeb,0xef,
        0x9e,0xbb,0x4b,0x90,0xb3,0x8a,0x5f,0x90,
        0x2e,0x83,0xfe,0x1b,0x13,0x5a,0x70,0xe2,
        0x3a,0xed,0x76,0x2e,0x97,0x10,0xa1,0x2e
    };
    uint8_t actual[32];
    mtk_wpa_pmk((const uint8_t *)"password", 8, (const uint8_t *)"IEEE", 4, actual);
    if (!mtk_ct_equal(actual, expected, 32)) {
        fputs("WPA2 IEEE PMK known-answer test FAILED\n", stderr);
        mtk_zero(actual, sizeof(actual));
        return 1;
    }
    mtk_zero(actual, sizeof(actual));
    printf("PASS: IEEE WPA2 PMK vector; ABI join=%zu scan=%zu status=%zu\n",
           sizeof(struct mtk_join_params), sizeof(struct mtk_scan_result), sizeof(struct mtk_status));
    return 0;
}

#ifndef _WIN32
#include <dlfcn.h>
#include <readpassphrase.h>
#include <unistd.h>

extern unsigned int mach_task_self_;
typedef int32_t result_t;
static uint32_t connection;
static void *framework;
static result_t (*close_service)(uint32_t);
static result_t (*call_method)(uint32_t, uint32_t, const uint64_t *, uint32_t,
    const void *, size_t, uint64_t *, uint32_t *, void *, size_t *);

static void cleanup(void) {
    if (connection && close_service) close_service(connection);
    connection = 0;
    if (framework) dlclose(framework);
    framework = NULL;
}

static void *symbol(const char *name) {
    void *p = dlsym(framework, name);
    if (!p) { fprintf(stderr, "Missing IOKit symbol: %s\n", name); exit(1); }
    return p;
}

static void open_driver(void) {
    framework = dlopen("/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit", RTLD_LAZY | RTLD_LOCAL);
    if (!framework) framework = dlopen("/System/Library/Frameworks/IOKit.framework/IOKit", RTLD_LAZY | RTLD_LOCAL);
    if (!framework) { fprintf(stderr, "Cannot open IOKit: %s\n", dlerror()); exit(1); }
    atexit(cleanup);
    void *(*matching)(const char *) = symbol("IOServiceMatching");
    uint32_t (*get_service)(uint32_t, void *) = symbol("IOServiceGetMatchingService");
    result_t (*open_service)(uint32_t, uint32_t, uint32_t, uint32_t *) = symbol("IOServiceOpen");
    result_t (*release_object)(uint32_t) = symbol("IOObjectRelease");
    close_service = symbol("IOServiceClose");
    call_method = symbol("IOConnectCallMethod");
    uint32_t service = get_service(0, matching("MtkWlan"));
    if (!service) {
        fputs("MtkWlan service not found. Check kext loading, PCI IDs and RP06 ACPI masking.\n", stderr);
        exit(2);
    }
    result_t r = open_service(service, mach_task_self_, 0, &connection);
    release_object(service);
    if (r) { fprintf(stderr, "IOServiceOpen failed: 0x%08x\n", (unsigned)r); exit(2); }
}

static void invoke(unsigned selector, const void *input, size_t input_size,
                   void *output, size_t *output_size) {
    result_t r = call_method(connection, selector, NULL, 0, input, input_size,
                             NULL, NULL, output, output_size);
    if (r) { fprintf(stderr, "Driver call %u failed: 0x%08x\n", selector, (unsigned)r); exit(2); }
}

static struct mtk_status status(void) {
    struct mtk_status s = {0};
    size_t n = sizeof(s);
    invoke(kMtkUcStatus, NULL, 0, &s, &n);
    if (n != sizeof(s) || s.version != MTK_USER_API_VERSION) {
        fputs("Unexpected driver ABI; refusing further commands.\n", stderr); exit(2);
    }
    return s;
}

static void print_ssid(const char *ssid, size_t len) {
    if (len > 32) len = 32;
    for (size_t i = 0; i < len; ++i) {
        unsigned char c = (unsigned char)ssid[i];
        if (c < 0x20 || c == 0x7f) printf("\\x%02x", c); else putchar(c);
    }
}

static void print_status(struct mtk_status s) {
    printf("state=%u link=%u port=%u frontend=%u channel=%u rssi=%d result=%u ssid=",
           s.state, s.link_up, s.port_open, s.front_end, s.channel, s.rssi, s.last_result);
    print_ssid(s.ssid, s.ssid_len);
    putchar('\n');
}

static void list_networks(void) {
    struct mtk_scan_result rows[MTK_SCAN_MAX];
    size_t n = sizeof(rows);
    invoke(kMtkUcResults, NULL, 0, rows, &n);
    if (n > sizeof(rows) || n % sizeof(rows[0])) { fputs("Invalid scan result size\n",stderr); exit(2); }
    puts("RSSI CH SECURITY JOINABLE SSID");
    for (size_t i = 0; i < n / sizeof(rows[0]); ++i) {
        struct mtk_scan_result *r = &rows[i];
        const char *sec = r->security == MTK_SEC_OPEN ? "OPEN" : r->security == MTK_SEC_RSN ? "RSN" : "LEGACY";
        printf("%4d %2u %-8s %-8s ", r->rssi, r->channel, sec, (r->flags & MTK_BSS_JOINABLE) ? "yes" : "no");
        print_ssid(r->ssid, r->ssid_len); putchar('\n');
    }
}

static int run(int argc, char **argv) {
    if (argc < 2) {
        fputs("Usage: mtkwifi-recovery status|scan|list|disconnect|join SSID [--open]|--selftest\n",stderr);
        return 1;
    }
    const char *cmd = argv[1];
    if (strcmp(cmd,"status") && strcmp(cmd,"scan") && strcmp(cmd,"list") && strcmp(cmd,"disconnect") && strcmp(cmd,"join")) {
        fputs("Unknown command\n",stderr); return 1;
    }
    if (!strcmp(cmd,"join") && (argc < 3 || argc > 4 || !strlen(argv[2]) || strlen(argv[2]) > 32 ||
            (argc == 4 && strcmp(argv[3],"--open")))) {
        fputs("Usage: mtkwifi-recovery join SSID [--open]; SSID must be 1..32 bytes.\n",stderr); return 1;
    }
    if (strcmp(cmd,"status") && strcmp(cmd,"list") && geteuid() != 0) {
        fputs("Run this command as root (Recovery Terminal already runs as root).\n",stderr); return 1;
    }
    open_driver();
    if (!strcmp(cmd,"status")) { print_status(status()); return 0; }
    if (!strcmp(cmd,"list")) { list_networks(); return 0; }
    if (!strcmp(cmd,"scan")) {
        invoke(kMtkUcScan,NULL,0,NULL,NULL);
        for (unsigned i=0; i<30; ++i) { sleep(1); if (!status().scanning) { list_networks(); return 0; } }
        fputs("Scan did not finish within 30 seconds\n",stderr); return 3;
    }
    if (!strcmp(cmd,"disconnect")) { invoke(kMtkUcDisconnect,NULL,0,NULL,NULL); return 0; }
    struct mtk_join_params p = {0};
    p.version = MTK_USER_API_VERSION; p.ssid_len = (uint8_t)strlen(argv[2]);
    memcpy(p.ssid,argv[2],p.ssid_len);
    if (argc != 4) {
        char pass[256] = {0};
        if (!readpassphrase("WPA2 password (hidden): ",pass,sizeof(pass),RPP_REQUIRE_TTY)) {
            mtk_zero(pass,sizeof(pass)); fputs("Cannot read password from terminal\n",stderr); return 1;
        }
        size_t len = strlen(pass);
        if (len < 8 || len > 63) { mtk_zero(pass,sizeof(pass)); fputs("WPA2 passphrase must be 8..63 bytes\n",stderr); return 1; }
        p.key_type = MTK_KEY_PMK;
        mtk_wpa_pmk((const uint8_t *)pass,len,p.ssid,p.ssid_len,p.pmk);
        mtk_zero(pass,sizeof(pass));
    }
    result_t r = call_method(connection,kMtkUcJoin,NULL,0,&p,sizeof(p),NULL,NULL,NULL,NULL);
    mtk_zero(&p,sizeof(p));
    if (r) { fprintf(stderr,"Join request failed: 0x%08x\n",(unsigned)r); return 2; }
    for (unsigned i=0; i<60; ++i) {
        sleep(1); struct mtk_status s=status();
        if (s.state == MTK_ST_CONNECTED && s.link_up && s.port_open) {
            print_status(s); puts("Associated. Request DHCP on the MtkWlan Ethernet interface next."); return 0;
        }
        if (s.last_result >= MTK_JOIN_NOT_FOUND && s.last_result <= MTK_JOIN_RSN_MISMATCH) {
            print_status(s); fputs("Join failed. Result 10 usually means a wrong password; 3/14 means unsupported security.\n",stderr); return 3;
        }
    }
    print_status(status()); fputs("Join did not complete within 60 seconds\n",stderr); return 3;
}
#endif

int main(int argc, char **argv) {
    if (argc == 2 && !strcmp(argv[1],"--selftest")) return selftest();
#ifdef _WIN32
    fputs("This host build supports --selftest only. Use the Mach-O build in macOS Recovery.\n",stderr);
    return 1;
#else
    return run(argc,argv);
#endif
}
