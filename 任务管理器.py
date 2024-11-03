import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import psutil


def list_processes(search_name="", filter_type="all"):
    for item in tree.get_children():
        tree.delete(item)

    for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'cpu_percent', 'num_threads']):
        if filter_type == "process" and not proc.info['name'].lower().endswith('.exe'):
            continue
        if filter_type == "software" and not proc.info['name'].lower().endswith('.exe'):
            continue
        if search_name and search_name not in proc.info['name'].lower():
            continue

        try:
            mem_usage = proc.info['memory_info'].rss / (1024 * 1024)  # Convert bytes to MB
            cpu_usage = proc.cpu_percent(interval=0.1)  # A brief interval to get CPU percent
            tree.insert("", "end", values=(
                proc.info['pid'],
                proc.info['name'],
                proc.info['username'],
                f"{mem_usage:.2f} MB",
                f"{cpu_usage} %",
                proc.info['num_threads']
            ))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def update_process_list(search_name="", filter_type="all"):
    threading.Thread(target=list_processes, args=(search_name, filter_type)).start()

def open_new_task_window():
    new_task_window = tk.Toplevel(root)
    new_task_window.title("新建任务")

    tk.Label(new_task_window, text="输入软件名称:").pack(pady=5)
    task_name_entry = tk.Entry(new_task_window)
    task_name_entry.pack(pady=5)

    search_button = tk.Button(new_task_window, text="打开", command=lambda: search_and_run(task_name_entry.get().strip()))
    search_button.pack(pady=5)

def search_and_run(task_name):
    if task_name:
        threading.Thread(target=start_task, args=(task_name,)).start()
    else:
        messagebox.showwarning("警告", "请输入软件名称")

#得行

def start_task(process_name: object):
    try:
        subprocess.Popen(['cmd.exe', '/c','start', process_name])
        messagebox.showinfo("信息", f"已尝试新建任务: {process_name}")
    except Exception as e:
        messagebox.showerror("错误", str(e))

def kill_process():
    selected_item = tree.selection()
    if selected_item:
        pid: str = tree.item(selected_item)['values'][0]  # 获取选中的进程 PID
        try:
            process = psutil.Process(pid)
            process.terminate()  # 尝试优雅地结束进程(牢玩家)
            process.wait(timeout=3)  # 等待进程结束
            messagebox.showinfo("成功", f"进程 {pid} 已成功关闭")
            update_process_list()  # 更新进程列表
        except psutil.NoSuchProcess:
            messagebox.showwarning("警告", "进程不存在")
        except psutil.AccessDenied:
            messagebox.showerror("错误", "无法关闭该进程（权限不足）")
        except Exception as e:
            messagebox.showerror("错误", f"关闭进程时出错: {e}")
    else:
        messagebox.showwarning("警告", "请先选择一个进程")

def search_processes():
    search_name = input_entry.get().strip().lower()
    filter_type = filter_var.get()
    update_process_list(search_name, filter_type)

root = tk.Tk()
root.title("任务管理器")

input_label = tk.Label(root, text="输入想检测的软件名称：")
input_label.pack(pady=5)

input_entry = tk.Entry(root)
input_entry.pack(pady=5)

filter_var = tk.StringVar(value="全部")
filter_label = tk.Label(root, text="选择过滤类型：")
filter_label.pack(pady=5)

filter_menu = ttk.Combobox(root, textvariable=filter_var, values=["全部", "进程", "软件"])
filter_menu.pack(pady=5)

search_button = tk.Button(root, text="搜索", command=search_processes)
search_button.pack(pady=5)

tree = ttk.Treeview(root, columns=("PID", "Name", "Username", "Memory", "CPU", "Threads"), show='headings', height=10)
tree.heading("PID", text="PID")
tree.heading("Name", text="名称")
tree.heading("Username", text="用户名")
tree.heading("Memory", text="内存使用")
tree.heading("CPU", text="CPU使用率")
tree.heading("Threads", text="线程数")
tree.pack(pady=5)

new_task_button = tk.Button(root, text="新建任务", command=open_new_task_window)
new_task_button.pack(pady=5)

kill_process_button = tk.Button(root, text="强行关闭选中进程", command=kill_process)
kill_process_button.pack(pady=5)

update_process_list()  # 初始加载进程列表
root.mainloop()