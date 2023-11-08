# from distutils.core import setup
from numpy.distutils.core import setup  # 用于配置和安装Python包
from Cython.Distutils import build_ext  # 构建扩展模块
from Cython.Build import cythonize  # 用于将.pyx编译成C扩展模块
import numpy  # 用于科学计算

import sys
print("setup", sys.path)

setup(
  name='monotonic_align',  # 指定包名
  # packages=["monotonic_align"],  # 指定包含的子包
  # package_dir={"monotonic_align":""},  # 指定包含的子包路径
  ext_modules=cythonize("core.pyx"),  # 指定要编译的.pyx文件
  include_dirs=[numpy.get_include()],  # 指定包含的头文件路径
  cmdclass={'build_ext':build_ext},  # 指定使用Cython的build_ext类来编译
)
