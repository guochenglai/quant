<h2 align="center"> Requirements </h2>

- Chrome
- Python 3.11.7
- Install [pipx](https://pipx.pypa.io/stable/installation/)
- Install [Poetry 1.8.1](https://python-poetry.org/docs/#installation): `pipx install poetry==1.8.1`
- Install [CUDA 121](https://developer.nvidia.com/cuda-12-1-0-download-archive)

<h2 align="center"> Init project </h2>

- Go to the root of this project
- Execute `poetry shell`
- Execute `python install.py`
   
<h2 align="center"> Setup your Futu env </h2>

- Note FutuD is for develop usage, it is different from Futu Client, but the account is same with Futu Client
- Download and install [FutuD](https://www.futunn.com/en/download/OpenAPI)
- Open FutuD setup the listen port to: 33333
- Execute `python install.py`




<h2 align="center"> Try it out </h2>

- Run `poetry run python .\quant\fetch_data.py` to train data
- Run `poetry run python .\quant\train_model.py` to train data
- Run `poetry run python .\quant\back_test.py` to test model
- Run `poetry run python .\quant\fetch_spy500_data.py` to download stock data for all spy company