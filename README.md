<h2 align="center"> Requirements </h2>

- Chrome
- Python 3.11.7
- Install [Poetry 1.8.1](https://python-poetry.org/docs/#installation): `pipx install poetry==1.8.1`
- Install [CUDA 121](https://developer.nvidia.com/cuda-12-1-0-download-archive)

<h2 align="center"> Try it out </h2>

- Run `poetry run python .\quant\fetch_data.py` to train data
- Run `poetry run python .\quant\train_model.py` to train data
- Run `poetry run python .\quant\back_test.py` to test model