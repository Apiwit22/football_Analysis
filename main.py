import tkinter as tk
import glob
from tkinter import filedialog, ttk, messagebox
from yolo_inference import run_tracking
from heatmap_plot import generate_heatmap
import os
import threading  # ✅ ใช้ Threading เพื่อแก้ปัญหา Not Responding

class FootballApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Tracking & Heatmap Generator")
        self.root.geometry("600x200")

        self.video_path = None
        self.heatmap_paths = []  # เก็บไฟล์ heatmap ทั้ง 3 รูป

        # ----- UI Layout -----
        self.create_widgets()

    def create_widgets(self):
        # Top Frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        btn_select = tk.Button(top_frame, text="🎥 เลือกวิดีโอ", command=self.select_video)
        btn_select.grid(row=0, column=0, padx=5)

        btn_track = tk.Button(top_frame, text="🏃‍♂️ Run Tracking", command=self.start_tracking_thread)
        btn_track.grid(row=0, column=1, padx=5)

        btn_heatmap = tk.Button(top_frame, text="🔥 Generate Heatmap", command=self.start_heatmap_thread)
        btn_heatmap.grid(row=0, column=2, padx=5)

        # Status
        self.status_label = tk.Label(self.root, text="🔄 Ready", anchor='w')
        self.status_label.pack(fill='x', pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=20)

    def select_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
        if path:
            self.video_path = path
            self.status_label.config(text=f"📂 เลือกไฟล์แล้ว: {os.path.basename(path)}")

    ### ✅ ใช้ Threading เพื่อป้องกัน UI ค้าง
    def start_tracking_thread(self):
        threading.Thread(target=self.run_tracking, daemon=True).start()

    def run_tracking(self):
        if not self.video_path:
            messagebox.showwarning("Missing video", "กรุณาเลือกไฟล์วิดีโอก่อน")
            return

        self.status_label.config(text="🏃‍♂️ กำลังรัน YOLO Tracking...")
        self.progress.start()

        try:
            run_tracking(self.video_path)  # 🏃‍♂️ Tracking
            self.status_label.config(text="✅ Tracking เสร็จสมบูรณ์แล้ว!")

            # หาไฟล์วิดีโอ output ล่าสุดจาก runs/detect
            predict_dirs = sorted(glob.glob('runs/detect/predict*'), key=os.path.getmtime, reverse=True)
            if predict_dirs:
                output_dir = predict_dirs[0]
                for f in os.listdir(output_dir):
                    if f.endswith('.mp4'):
                        tracked_video_path = os.path.join(output_dir, f)
                        self.root.after(0, lambda: self.save_tracked_video(tracked_video_path))
                        break

        except Exception as e:
            messagebox.showerror("Tracking Error", str(e))
            self.status_label.config(text="❌ เกิดข้อผิดพลาดขณะ Tracking")
        finally:
            self.progress.stop()

    def save_tracked_video(self, video_path):
        if not os.path.exists(video_path):  # ❌ ไฟล์ต้นฉบับหาย
            messagebox.showerror("Error", "❌ ไฟล์วิดีโอที่ต้องการบันทึกไม่มีอยู่จริง!")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")],
            title="เลือกที่บันทึกวิดีโอ"
        )

        if not save_path:  # ❌ ถ้าผู้ใช้กดยกเลิก
            messagebox.showwarning("Warning", "⚠️ คุณไม่ได้เลือกที่บันทึกไฟล์วิดีโอ")
            return

        if os.path.exists(save_path):  # ⚠️ ถ้าไฟล์ปลายทางมีอยู่แล้ว ให้ถามก่อนเขียนทับ
            confirm = messagebox.askyesno("Confirm Overwrite", f"⚠️ ไฟล์ {os.path.basename(save_path)} มีอยู่แล้ว\nคุณต้องการเขียนทับหรือไม่?")
            if not confirm:
                return  # ❌ ไม่เขียนทับ

        try:
            os.rename(video_path, save_path)  # ✅ บันทึกไฟล์
            messagebox.showinfo("✅ บันทึกวิดีโอสำเร็จ", f"วิดีโอบันทึกที่:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"❌ ไม่สามารถบันทึกวิดีโอได้:\n{e}")

    ### ✅ ใช้ Threading เพื่อป้องกัน UI ค้าง
    def start_heatmap_thread(self):
        threading.Thread(target=self.run_heatmap, daemon=True).start()

    def run_heatmap(self):
        self.status_label.config(text="🔥 กำลังสร้าง Heatmap สำหรับทั้ง 3 ทีม...")
        self.progress.start()

        try:
            # สร้าง heatmap 3 แบบ
            self.heatmap_paths = [
                generate_heatmap("team1"),
                generate_heatmap("team2"),
                generate_heatmap("both")
            ]

            self.status_label.config(text="✅ สร้าง Heatmap สำเร็จแล้ว!")
            self.root.after(0, self.save_heatmap_files)  # ใช้ after() เพื่อเรียก UI event

        except Exception as e:
            messagebox.showerror("Heatmap Error", str(e))
            self.status_label.config(text="❌ เกิดข้อผิดพลาดขณะสร้าง Heatmap")
        finally:
            self.progress.stop()

    def save_heatmap_files(self):
        save_dir = filedialog.askdirectory(title="เลือกโฟลเดอร์สำหรับบันทึก Heatmap")

        if not save_dir:  # ❌ ถ้าผู้ใช้กดยกเลิก
            messagebox.showwarning("Warning", "⚠️ คุณไม่ได้เลือกโฟลเดอร์สำหรับบันทึก Heatmap")
            return

        failed_saves = []  # 📌 เก็บรายชื่อไฟล์ที่บันทึกไม่สำเร็จ

        for heatmap in self.heatmap_paths:
            if not os.path.exists(heatmap):  # ❌ ไฟล์ heatmap ไม่มีอยู่
                failed_saves.append(os.path.basename(heatmap))
                continue  # ข้ามไฟล์นี้ไป

            save_path = os.path.join(save_dir, os.path.basename(heatmap))

            if os.path.exists(save_path):  # ⚠️ ถ้าไฟล์ปลายทางมีอยู่แล้ว ให้ถามก่อนเขียนทับ
                confirm = messagebox.askyesno("Confirm Overwrite", f"⚠️ ไฟล์ {os.path.basename(save_path)} มีอยู่แล้ว\nคุณต้องการเขียนทับหรือไม่?")
                if not confirm:
                    continue  # ❌ ข้ามไฟล์นี้ไป

            try:
                os.rename(heatmap, save_path)  # ✅ บันทึกไฟล์
            except Exception as e:
                failed_saves.append(os.path.basename(heatmap))

        if failed_saves:
            messagebox.showwarning("Warning", f"⚠️ บันทึก Heatmap บางไฟล์ไม่สำเร็จ:\n{', '.join(failed_saves)}")
        else:
            messagebox.showinfo("✅ บันทึกสำเร็จ", f"Heatmap ถูกบันทึกที่:\n{save_dir}")


# -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = FootballApp(root)
    root.mainloop()
