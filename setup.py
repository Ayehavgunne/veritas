from distutils.core import setup

setup(
    name="tabularpy",
    version="1.0.4rc2",
    description="Python tablular information manipulation library",
    author="Anthony Post",
    author_email="postanthony3000@gmail.com",
    url="https://github.com/Ayehavgunne/veritas/",
    packages=["tabularpy"],
    extras_require={
        "dist": ["dateutil", "BeautifulSoup4"],
        "dev": ["pytest", "pylint"],
    },
)
