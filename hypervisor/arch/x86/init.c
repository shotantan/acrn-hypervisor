/*
 * Copyright (C) 2018-2022 Intel Corporation.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include <types.h>
#include <asm/init.h>
#include <console.h>
#include <asm/per_cpu.h>
#include <shell.h>
#include <asm/vmx.h>
#include <asm/guest/vm.h>
#include <logmsg.h>

#pragma GCC diagnostic ignored "-Wunused-function"
static void delay_n_sec(uint64_t sec) {
    if (sec == 0) return;
    uint64_t start, current;
    asm volatile("rdtsc\n\tshl $32, %%rdx\n\tor %%rdx, %%rax" : "=a" (start) : : "rdx");
    while (1) {
        asm volatile("rdtsc\n\tshl $32, %%rdx\n\tor %%rdx, %%rax" : "=a" (current) : : "rdx");
        if ((current - start) > (sec * 2000000000ULL)) { // Approx 2GHz
            break;
        }
        asm volatile("pause");
    }
}
static void trap_reboot(uint64_t sec) {
    delay_n_sec(sec);
    asm volatile("movb $0x11, %al; movw $0x0cf9, %dx; outb %al, %dx");
}

/* 
 * BISECTION TRAP CONFIGURATION
 * Set ACTIVE_TRAP to choose which point to reboot at.
 */
#define ACTIVE_TRAP 0

#include <asm/seed.h>

#include <asm/boot/ld_sym.h>
#include <boot.h>

/* boot_regs store the multiboot info magic and address, defined in
   arch/x86/boot/cpu_primary.S.
   */
extern uint32_t boot_regs[2];

/* Push sp magic to top of stack for call trace */
#define SWITCH_TO(rsp, to)                                              \
{                                                                       \
	asm volatile ("movq %0, %%rsp\n"                                \
			"pushq %1\n"                                    \
			"jmpq *%2\n"                                    \
			 :                                              \
			 : "r"(rsp), "rm"(SP_BOTTOM_MAGIC), "a"(to));   \
}

/*TODO: move into debug module */
static void init_debug_pre(void)
{
	/* Initialize console */
	console_init();

	/* Enable logging */
	init_logmsg();
}

/*TODO: move into debug module */
static void init_debug_post(uint16_t pcpu_id)
{
	if (pcpu_id == BSP_CPU_ID) {
		/* Initialize the shell */
		shell_init();
	}

	if (pcpu_id == VUART_TIMER_CPU) {
		console_setup_timer();
	}

	profiling_setup();
}

/*TODO: move into guest-vcpu module */
static void init_guest_mode(uint16_t pcpu_id)
{
	vmx_on();

	launch_vms(pcpu_id);
}

static void init_pcpu_comm_post(void)
{
	uint16_t pcpu_id;

	pcpu_id = get_pcpu_id();

	init_pcpu_post(pcpu_id);
	init_debug_post(pcpu_id);
	init_guest_mode(pcpu_id);
	run_idle_thread();
}

static void init_misc(void)
{
	init_cr0_cr4_flexible_bits();
	if (!sanitize_cr0_cr4_pattern()) {
		panic("%s Sanitize pattern of CR0 or CR4 failed.\n", __func__);
	}
}

/* NOTE: this function is using temp stack, and after SWITCH_TO(runtime_sp, to)
 * it will switch to runtime stack.
 */
void init_primary_pcpu(void)
{
	uint64_t rsp;

	/* Clear BSS */
	(void)memset(&ld_bss_start, 0U, (size_t)(&ld_bss_end - &ld_bss_start));

	init_acrn_boot_info(boot_regs);
#if ACTIVE_TRAP == 5
        trap_reboot(5);
#endif

	init_debug_pre();
#if ACTIVE_TRAP == 10
        trap_reboot(10);
#endif

	if (sanitize_acrn_boot_info(get_acrn_boot_info()) != 0) {
		panic("Sanitize boot info failed!");
	}

	init_pcpu_pre(true);
#if ACTIVE_TRAP == 15
        trap_reboot(15);
#endif

	init_seed();
#if ACTIVE_TRAP == 20
        trap_reboot(20);
#endif
	init_misc();
#if ACTIVE_TRAP == 25
        trap_reboot(25);
#endif

	/* Switch to run-time stack */
	rsp = (uint64_t)(&get_cpu_var(stack)[CONFIG_STACK_SIZE - 1]);
	rsp &= ~(CPU_STACK_ALIGN - 1UL);
	#if ACTIVE_TRAP == 30
        trap_reboot(30);
#endif
        SWITCH_TO(rsp, init_pcpu_comm_post);
}

void init_secondary_pcpu(void)
{
	init_pcpu_pre(false);
	init_pcpu_comm_post();
}
