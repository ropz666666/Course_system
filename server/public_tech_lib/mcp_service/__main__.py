import asyncio
import sys
project_root = "E:/virtual_teacher_server"  # 根据实际结构调整
sys.path.append(str(project_root))
from server import main
sys.exit(main())
