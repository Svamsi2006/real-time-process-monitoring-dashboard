import psutil

def get_system_stats():
    cpu_usage = round(psutil.cpu_percent(), 2)
    memory_usage = round(psutil.virtual_memory().percent, 2)
    disk_usage = round(psutil.disk_usage('/').percent, 2)
    return cpu_usage, memory_usage, disk_usage

def get_process_list(search_text=""):
    search_text = search_text.lower().strip()
    processes = (
        (p.info["pid"], p.info["name"], round(p.info["cpu_percent"] or 0.0, 2), round(p.info["memory_percent"] or 0.0, 2))
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"])
    )
    sorted_processes = sorted(processes, key=lambda x: x[2], reverse=True)

    if search_text:
        sorted_processes = filter(lambda p: search_text in p[1].lower(), sorted_processes)

    return list(sorted_processes)

def terminate_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        return True, f"Process {pid} terminated successfully."
    except psutil.NoSuchProcess:
        return False, f"Process {pid} does not exist."
    except psutil.AccessDenied:
        return False, f"Permission denied to terminate process {pid}."
    except Exception as e:
        return False, f"Failed to terminate process {pid}: {str(e)}"
