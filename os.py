"""
Operating Systems SLA Stage-2: Memory Allocation Simulation
Algorithm: Threshold-Aware Best-Fit (TABF) / Adaptive Hybrid Allocation Policy (AHAP)
Research Reference: Chen, L., Zhang, Y., & Kumar, R. (2023)
Department of Computer Engineering, SAKEC
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TABFSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Memory Allocator: Threshold-Aware Best-Fit (TABF) Simulator")
        self.root.geometry("1080x780")
        self.root.minsize(980, 700)
        self.root.configure(bg="#0f172a")  # Slate-900 background

        # Core State Variables
        self.initial_blocks = [100, 500, 200, 300, 600]
        self.blocks = list(self.initial_blocks)
        self.block_occupied = [0] * len(self.blocks)
        self.allocations = [[] for _ in self.blocks]
        
        self.process_queue = [190, 417, 112, 426]
        self.threshold = 16
        self.current_proc_idx = 0

        # Stats
        self.success_count = 0
        self.rejection_count = 0
        self.dust_avoided_count = 0
        self.total_internal_frag = 0

        self.setup_ui()
        self.reset_simulation()

    def setup_ui(self):
        # Header Frame
        header = tk.Frame(self.root, bg="#1e293b", padx=20, pady=12)
        header.pack(fill=tk.X)

        title_lbl = tk.Label(
            header,
            text="Threshold-Aware Best-Fit (TABF) Memory Allocator",
            font=("Segoe UI", 16, "bold"),
            fg="#f8fafc",
            bg="#1e293b"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header,
            text="Research Implementation: Chen, Zhang, & Kumar (2023) | Dynamic Split-Threshold Model (θ)",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b"
        )
        subtitle_lbl.pack(anchor="w")

        # Top Configuration Frame
        config_frame = tk.LabelFrame(
            self.root,
            text=" Configuration & Workload Parameters ",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
            padx=15,
            pady=10
        )
        config_frame.pack(fill=tk.X, padx=16, pady=10)

        # Config Inputs Grid
        tk.Label(config_frame, text="Memory Blocks (KB):", font=("Segoe UI", 9, "bold"), fg="#e2e8f0", bg="#1e293b").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.entry_blocks = tk.Entry(config_frame, width=32, font=("Consolas", 10), bg="#334155", fg="#f8fafc", insertbackground="white")
        self.entry_blocks.grid(row=0, column=1, padx=5, pady=4)
        self.entry_blocks.insert(0, "100, 500, 200, 300, 600")

        tk.Label(config_frame, text="Incoming Processes (KB):", font=("Segoe UI", 9, "bold"), fg="#e2e8f0", bg="#1e293b").grid(row=0, column=2, sticky="w", padx=10, pady=4)
        self.entry_procs = tk.Entry(config_frame, width=28, font=("Consolas", 10), bg="#334155", fg="#f8fafc", insertbackground="white")
        self.entry_procs.grid(row=0, column=3, padx=5, pady=4)
        self.entry_procs.insert(0, "190, 417, 112, 426")

        tk.Label(config_frame, text="Split Threshold θ (KB):", font=("Segoe UI", 9, "bold"), fg="#e2e8f0", bg="#1e293b").grid(row=0, column=4, sticky="w", padx=10, pady=4)
        self.entry_thresh = tk.Entry(config_frame, width=8, font=("Consolas", 10), bg="#334155", fg="#f8fafc", insertbackground="white")
        self.entry_thresh.grid(row=0, column=5, padx=5, pady=4)
        self.entry_thresh.insert(0, "16")

        # Action Buttons
        btn_frame = tk.Frame(config_frame, bg="#1e293b")
        btn_frame.grid(row=1, column=0, columnspan=6, sticky="w", pady=(8, 2), padx=5)

        self.btn_load = tk.Button(btn_frame, text="Apply Configuration", font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="white", activebackground="#0369a1", activeforeground="white", command=self.load_inputs, padx=10, relief=tk.FLAT)
        self.btn_load.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_step = tk.Button(btn_frame, text="▶ Step Forward", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="white", activebackground="#059669", activeforeground="white", command=self.step_forward, padx=10, relief=tk.FLAT)
        self.btn_step.pack(side=tk.LEFT, padx=6)

        self.btn_run = tk.Button(btn_frame, text="⚡ Run All", font=("Segoe UI", 9, "bold"), bg="#6366f1", fg="white", activebackground="#4f46e5", activeforeground="white", command=self.run_all, padx=10, relief=tk.FLAT)
        self.btn_run.pack(side=tk.LEFT, padx=6)

        self.btn_reset = tk.Button(btn_frame, text="↺ Reset", font=("Segoe UI", 9, "bold"), bg="#64748b", fg="white", activebackground="#475569", activeforeground="white", command=self.reset_simulation, padx=10, relief=tk.FLAT)
        self.btn_reset.pack(side=tk.LEFT, padx=6)

        # Legend Bar
        legend_frame = tk.Frame(btn_frame, bg="#1e293b")
        legend_frame.pack(side=tk.RIGHT, padx=10)
        self.create_legend_item(legend_frame, "#2563eb", "Allocated Process")
        self.create_legend_item(legend_frame, "#10b981", "Usable Free Space")
        self.create_legend_item(legend_frame, "#d97706", "Dust Prevented (Internal Frag)")

        # Memory Map Visualizer Canvas
        vis_frame = tk.LabelFrame(
            self.root,
            text=" Real-Time Physical Memory Map ",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
            padx=12,
            pady=8
        )
        vis_frame.pack(fill=tk.X, padx=16, pady=4)

        self.canvas = tk.Canvas(vis_frame, height=130, bg="#0b1120", highlightthickness=1, highlightbackground="#334155")
        self.canvas.pack(fill=tk.X, expand=True, pady=4)

        # Bottom Split Area: Analytics (Left) and Event Log (Right)
        bottom_frame = tk.Frame(self.root, bg="#0f172a")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # Left Column: Analytics Cards
        analytics_frame = tk.LabelFrame(
            bottom_frame,
            text=" Live Analytics & Metrics ",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
            padx=12,
            pady=10,
            width=340
        )
        analytics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 8))
        analytics_frame.pack_propagate(False)

        self.lbl_ext_frag = self.create_metric_card(analytics_frame, "External Fragmentation (Φext):", "0.0%", "#f87171")
        self.lbl_success = self.create_metric_card(analytics_frame, "Allocation Success Rate:", "0 / 0 (100%)", "#34d399")
        self.lbl_dust = self.create_metric_card(analytics_frame, "Micro-Holes Prevented:", "0 instances", "#fbbf24")
        self.lbl_int_frag = self.create_metric_card(analytics_frame, "Bounded Internal Frag:", "0 KB", "#93c5fd")
        self.lbl_free_mem = self.create_metric_card(analytics_frame, "Total Free Contiguous RAM:", "1700 KB", "#38bdf8")

        # Right Column: Event Log Console
        log_frame = tk.LabelFrame(
            bottom_frame,
            text=" Allocation Event & Trace Console ",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#1e293b",
            padx=10,
            pady=10
        )
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        self.log_text = tk.Text(
            log_frame,
            bg="#020617",
            fg="#e2e8f0",
            font=("Consolas", 9),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Log Text Styling
        self.log_text.tag_config("timestamp", foreground="#64748b")
        self.log_text.tag_config("info", foreground="#38bdf8")
        self.log_text.tag_config("match", foreground="#93c5fd")
        self.log_text.tag_config("suppress", foreground="#fbbf24", font=("Consolas", 9, "bold"))
        self.log_text.tag_config("split", foreground="#34d399")
        self.log_text.tag_config("reject", foreground="#f87171", font=("Consolas", 9, "bold"))

    def create_legend_item(self, parent, color, text):
        box = tk.Label(parent, bg=color, width=2, height=1)
        box.pack(side=tk.LEFT, padx=(6, 2))
        lbl = tk.Label(parent, text=text, font=("Segoe UI", 8), fg="#cbd5e1", bg="#1e293b")
        lbl.pack(side=tk.LEFT, padx=(0, 6))

    def create_metric_card(self, parent, title, initial_val, val_color):
        card = tk.Frame(parent, bg="#334155", padx=8, pady=6)
        card.pack(fill=tk.X, pady=4)
        t_lbl = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#94a3b8", bg="#334155")
        t_lbl.pack(anchor="w")
        v_lbl = tk.Label(card, text=initial_val, font=("Segoe UI", 12, "bold"), fg=val_color, bg="#334155")
        v_lbl.pack(anchor="w")
        return v_lbl

    def log(self, message, tag="info"):
        ts = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.insert(tk.END, ts, "timestamp")
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)

    def load_inputs(self):
        try:
            raw_blocks = [int(x.strip()) for x in self.entry_blocks.get().split(",") if x.strip()]
            raw_procs = [int(x.strip()) for x in self.entry_procs.get().split(",") if x.strip()]
            thresh = int(self.entry_thresh.get().strip())

            if not raw_blocks or not raw_procs or thresh < 0:
                raise ValueError("Invalid numbers")

            self.initial_blocks = raw_blocks
            self.process_queue = raw_procs
            self.threshold = thresh
            self.reset_simulation()
            self.log(f"Configuration applied: {len(self.initial_blocks)} blocks, {len(self.process_queue)} processes, θ = {self.threshold} KB", "info")
        except Exception:
            messagebox.showerror("Invalid Input", "Please enter valid comma-separated positive integers for blocks/processes and a non-negative threshold.")

    def reset_simulation(self):
        self.blocks = list(self.initial_blocks)
        self.block_occupied = [0] * len(self.blocks)
        self.allocations = []
        for size in self.blocks:
            self.allocations.append([{'type': 'free', 'size': size, 'label': f'Free: {size}K'}])

        self.current_proc_idx = 0
        self.success_count = 0
        self.rejection_count = 0
        self.dust_avoided_count = 0
        self.total_internal_frag = 0

        self.log_text.delete(1.0, tk.END)
        self.log("=== Simulation Initialized: Threshold-Aware Best-Fit (TABF) ===", "info")
        self.log(f"Initial Partitions: {self.initial_blocks} | Dynamic Split Threshold θ: {self.threshold} KB", "info")
        self.log(f"Workload Process Requests: {self.process_queue}\n", "info")

        self.btn_step.config(state=tk.NORMAL)
        self.btn_run.config(state=tk.NORMAL)

        self.update_metrics()
        self.draw_memory_map()

    def step_forward(self):
        if self.current_proc_idx >= len(self.process_queue):
            self.log("All incoming processes have been evaluated.", "info")
            self.btn_step.config(state=tk.DISABLED)
            self.btn_run.config(state=tk.DISABLED)
            return

        proc_id = self.current_proc_idx + 1
        proc_size = self.process_queue[self.current_proc_idx]

        best_idx = -1
        min_diff = 9999999

        # 1. Best-Fit Search across available unallocated partitions
        for j in range(len(self.blocks)):
            if self.block_occupied[j] == 0 and self.blocks[j] >= proc_size:
                diff = self.blocks[j] - proc_size
                if diff < min_diff:
                    min_diff = diff
                    best_idx = j

        # 2. Threshold-Aware Allocation
        if best_idx != -1:
            initial_block_capacity = self.blocks[best_idx]
            residual = initial_block_capacity - proc_size
            self.success_count += 1

            self.log(f"Process P{proc_id} ({proc_size} KB) -> Matched Block B{best_idx + 1} ({initial_block_capacity} KB)", "match")

            if residual <= self.threshold:
                # Suppress Split
                self.dust_avoided_count += 1
                self.total_internal_frag += residual
                self.blocks[best_idx] = 0
                self.block_occupied[best_idx] = 1

                self.allocations[best_idx] = [
                    {'type': 'allocated', 'size': proc_size, 'label': f'P{proc_id} ({proc_size}K)'}
                ]
                if residual > 0:
                    self.allocations[best_idx].append(
                        {'type': 'dust', 'size': residual, 'label': f'Dust Avoided ({residual}K)'}
                    )

                self.log(f"  └─ [Action]: Residual ({residual} KB) <= Threshold ({self.threshold} KB) -> SPLIT SUPPRESSED!", "suppress")
                self.log(f"  └─ [Result]: Entire {initial_block_capacity} KB assigned to P{proc_id}. Internal Frag: {residual} KB (Micro-hole avoided)", "suppress")
            else:
                # Normal Split
                self.blocks[best_idx] = residual
                self.allocations[best_idx] = [
                    {'type': 'allocated', 'size': proc_size, 'label': f'P{proc_id} ({proc_size}K)'},
                    {'type': 'free', 'size': residual, 'label': f'Free ({residual}K)'}
                ]

                self.log(f"  └─ [Action]: Residual ({residual} KB) > Threshold ({self.threshold} KB) -> NORMAL SPLIT", "split")
                self.log(f"  └─ [Result]: Allocated {proc_size} KB to P{proc_id}. Remaining usable hole in B{best_idx + 1}: {residual} KB", "split")

        else:
            self.rejection_count += 1
            self.log(f"Process P{proc_id} ({proc_size} KB) -> [REJECTED]: No contiguous free partition is large enough!", "reject")

        self.current_proc_idx += 1
        if self.current_proc_idx >= len(self.process_queue):
            self.btn_step.config(state=tk.DISABLED)
            self.btn_run.config(state=tk.DISABLED)

        self.update_metrics()
        self.draw_memory_map()

    def run_all(self):
        while self.current_proc_idx < len(self.process_queue):
            self.step_forward()

    def update_metrics(self):
        total_free = sum(self.blocks[j] for j in range(len(self.blocks)) if self.block_occupied[j] == 0)
        largest_free = max([self.blocks[j] for j in range(len(self.blocks)) if self.block_occupied[j] == 0], default=0)

        # External Fragmentation Index Φext = 1 - (Largest Free Block / Total Free Memory)
        if total_free > 0:
            phi_ext = (1.0 - (largest_free / total_free)) * 100.0
        else:
            phi_ext = 0.0

        total_attempted = self.current_proc_idx
        success_rate = (self.success_count / total_attempted * 100.0) if total_attempted > 0 else 100.0

        self.lbl_ext_frag.config(text=f"{phi_ext:.1f}%")
        self.lbl_success.config(text=f"{self.success_count}/{total_attempted} ({success_rate:.0f}%)")
        self.lbl_dust.config(text=f"{self.dust_avoided_count} avoided")
        self.lbl_int_frag.config(text=f"{self.total_internal_frag} KB")
        self.lbl_free_mem.config(text=f"{total_free} KB")

    def draw_memory_map(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        c_width = self.canvas.winfo_width()
        if c_width <= 1:
            c_width = 1000

        margin_x = 15
        usable_width = c_width - (2 * margin_x)
        total_initial_capacity = sum(self.initial_blocks)
        if total_initial_capacity == 0:
            return

        current_x = margin_x
        bar_y1 = 30
        bar_y2 = 95

        for i, init_size in enumerate(self.initial_blocks):
            block_width = (init_size / total_initial_capacity) * usable_width
            block_end_x = current_x + block_width

            # Partition boundary box & header label
            self.canvas.create_rectangle(current_x, bar_y1, block_end_x, bar_y2, outline="#475569", width=2)
            self.canvas.create_text(
                current_x + 4, bar_y1 - 12,
                text=f"B{i+1}: {init_size}K",
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                fill="#94a3b8"
            )

            # Segments within partition
            seg_x = current_x
            items = self.allocations[i]
            for item in items:
                seg_width = (item['size'] / init_size) * block_width
                seg_end_x = seg_x + seg_width

                fill_color = "#10b981"  # Usable Free (Emerald)
                if item['type'] == 'allocated':
                    fill_color = "#2563eb"  # Allocated Process (Blue)
                elif item['type'] == 'dust':
                    fill_color = "#d97706"  # Split Suppressed / Dust Avoided (Amber)

                self.canvas.create_rectangle(seg_x, bar_y1, seg_end_x, bar_y2, fill=fill_color, outline="#1e293b", width=1)
                
                # Label inside slice
                if seg_width > 35:
                    self.canvas.create_text(
                        (seg_x + seg_end_x) / 2, (bar_y1 + bar_y2) / 2,
                        text=item['label'],
                        font=("Segoe UI", 8, "bold"),
                        fill="#ffffff"
                    )
                seg_x = seg_end_x

            # Base synthetic address tag
            self.canvas.create_text(
                current_x, bar_y2 + 12,
                text=f"0x{int(current_x * 4):04X}",
                font=("Consolas", 8),
                anchor="w",
                fill="#64748b"
            )

            current_x = block_end_x

if __name__ == "__main__":
    root = tk.Tk()
    app = TABFSimulatorGUI(root)
    root.mainloop()