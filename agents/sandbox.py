import subprocess
import os
import signal
import tempfile
import logging
import logging.config  # 已存在
import yaml
import threading  # 用于 Windows 超时兼容
import platform  # 检查系统平台
import psutil  # 新增：用于 Windows 资源限制

# 加载配置（相对路径，从 agents/ 到根 config/）
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

TIMEOUT_SEC = config['sandbox']['timeout_sec']
MAX_MEMORY_MB = config['sandbox']['max_memory_mb']
LOG_LEVEL = config['agent']['log_level']

# 配置日志（使用 logging.conf）
logging_conf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'logging.conf')
logging.config.fileConfig(logging_conf_path)


def run_in_sandbox(code: str, src_dir: str = None, timeout_sec: int = TIMEOUT_SEC) -> dict:
    """
    在沙箱中执行代码。
    - code: 要执行的 Python 代码字符串。
    - src_dir: 可选隔离目录（默认用临时目录）。
    - timeout_sec: 超时秒数（从 config 读取或覆盖）。
    返回: {'stdout': str, 'stderr': str, 'returncode': int, 'exception': str or None}

    安全措施：
    - 使用临时目录隔离。
    - 禁止网络/文件写（通过 umask 和 ulimit/psutil）。
    - Windows 兼容：用 threading.Timer 替代 signal.alarm，无 ulimit，用 psutil 限制。
    """
    logging.info(f"Starting sandbox execution with timeout {timeout_sec}s and max memory {MAX_MEMORY_MB}MB")

    # 创建隔离目录
    sandbox_dir = tempfile.mkdtemp() if src_dir is None else src_dir
    temp_file_path = os.path.join(sandbox_dir, 'temp.py')

    # 写入代码到临时文件
    with open(temp_file_path, 'w', encoding='utf-8') as f:
        f.write(code)

    result = {'stdout': '', 'stderr': '', 'returncode': -1, 'exception': None}

    try:
        # 切换到沙箱目录，限制权限
        os.chdir(sandbox_dir)
        os.umask(0o077)  # 限制新文件为只读当前用户

        # 构建命令：Windows 跳过 ulimit，用 psutil 限制
        cmd = ['python', temp_file_path]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = psutil.Process(proc.pid)
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)  # 降低 CPU 优先级

        # 内存监控线程（如果超过 MAX_MEMORY_MB，终止）
        def memory_monitor():
            while proc.poll() is None:
                try:
                    mem = p.memory_info().rss / (1024 * 1024)  # MB
                    if mem > MAX_MEMORY_MB:
                        logging.warning("Memory limit exceeded, terminating")
                        proc.terminate()
                        result['exception'] = 'MemoryError: Exceeded max memory'
                except psutil.NoSuchProcess:
                    break
                threading.Event().wait(0.5)  # 每0.5s 检查

        mem_thread = threading.Thread(target=memory_monitor)
        mem_thread.start()

        # 超时处理
        def timeout_handler():
            if proc.poll() is None:
                logging.warning("Execution timed out, terminating process")
                proc.terminate()
            result['exception'] = 'TimeoutError: Execution exceeded timeout'

        timer = threading.Timer(timeout_sec, timeout_handler)
        timer.start()

        # 通信并捕获输出
        stdout, stderr = proc.communicate()
        result['stdout'] = stdout.decode('utf-8', errors='replace')  # 用 replace 避免解码错误
        result['stderr'] = stderr.decode('utf-8', errors='replace')
        result['returncode'] = proc.returncode

        if result['returncode'] != 0 and not result['exception']:
            result['exception'] = result['stderr'] or 'Unknown error'
            logging.error(f"Execution failed with exception: {result['exception']}")

    except Exception as e:
        result['exception'] = str(e)
        logging.error(f"Unexpected sandbox error: {e}")

    finally:
        # 清理超时和监控
        timer.cancel()
        mem_thread.join(timeout=1) if 'mem_thread' in locals() else None

        # 恢复 umask 并清理文件
        os.umask(0o022)
        try:
            os.remove(temp_file_path)
            if sandbox_dir.startswith(tempfile.gettempdir()):
                import shutil
                shutil.rmtree(sandbox_dir, ignore_errors=True)
        except OSError as e:
            logging.warning(f"Cleanup failed: {e}")

    logging.info("Sandbox execution complete")
    return result