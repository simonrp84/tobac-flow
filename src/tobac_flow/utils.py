import numpy as np
import scipy.ndimage as ndi
import xarray as xr
import pathlib
from datetime import datetime
from dateutil.parser import parse as parse_date
from typing import Callable

def get_dates_from_filename(filename: str | pathlib.Path) -> tuple[datetime, datetime]:
    if isinstance(filename, str):
        start_date = parse_date(filename.split("/")[-1].split("_S")[-1][:15], fuzzy=True)
        end_date = parse_date(filename.split("/")[-1].split("_E")[-1][:15], fuzzy=True)
    elif isinstance(filename, pathlib.Path):
        start_date = parse_date(filename.name.split("_S")[-1][:15], fuzzy=True)
        end_date = parse_date(filename.name.split("_E")[-1][:15], fuzzy=True)
    else:
        raise ValueError("filename parameter must be either a string or a Path object")
    
    return start_date, end_date

def trim_file_start(dataset: xr.Dataset, filename: str | pathlib.Path) -> xr.Dataset:
    return dataset.sel(t=slice(get_dates_from_filename(filename)[0], None))

def trim_file_end(dataset: xr.Dataset, filename: str | pathlib.Path) -> xr.Dataset:
    return dataset.sel(t=slice(None, get_dates_from_filename(filename)[1]))

def labeled_comprehension(
    field: np.ndarray,
    labels: np.ndarray[int],
    func: Callable,
    index: list[int] | None = None,
    dtype: type | None = None,
    default: float | None = None,
    pass_positions: bool = False,
) -> np.ndarray:
    """
    Wrapper for the scipy.ndimage.labeled_comprehension function

    Parameters
    ----------
    field : numpy.ndarray
        Data to apply the function overlap
    labels : numpy.ndarray
        The array of labeled regions
    func : function
        The function to apply to each labelled region
    index : list, optional (default : None)
        The label values to apply the comprehension over. Default value of None
            will apply the comprehension to all labels
    dtype : type, optional (default : None)
        The dtype of the output. Defaults to that of the input field
    default : scalar, optional (default : None)
        The value to return if a label does not exist
    pass_positions : bool, optional (default : False)
        If true, will pass the indexes of the label locations to the funtion in
            labeled_comprehension

    Returns
    -------
    comp : numpy.ndarray
        An array of the result of func applied to each labelled region included
            in index
    """
    if not dtype:
        dtype = field.dtype

    if not index:
        index = range(1, int(np.nanmax(labels)) + 1)

    comp = ndi.labeled_comprehension(
        field, labels, index, func, dtype, default, pass_positions
    )

    return comp
