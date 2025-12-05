import xarray as xr
from pooch import retrieve
from requests.exceptions import ReadTimeout

def download_OCADS_data(variables, scenarios):
    """
    Download multiple variables and scenarios from OCADS.

    Usage:
        data = download_OCADS_data(['pHT', 'Temperature'], ['historical', 'ssp585'])

    Returns:
        Nested dictionary of xarray.DataArray objects structured as:
            data[variable][scenario] → DataArray

    Available variables:
        - Aragonite
        - CO3
        - Calcite
        - DIC
        - H
        - Hfree
        - RF
        - Salinity
        - TA
        - Temperature
        - fCO2
        - pCO2
        - pHT

    Available scenarios:
        - historical
        - ssp119
        - ssp126
        - ssp245
        - ssp370
        - ssp585
    """

    def pooch_load(url, filename):
        return retrieve(url=url, known_hash=None, fname=filename)

    # Normalize inputs
    if isinstance(variables, str):
        variables = [variables]
    if isinstance(scenarios, str):
        scenarios = [scenarios]

    available_variables = [
        "Aragonite", "CO3", "Calcite", "DIC", "H", "Hfree", "RF",
        "Salinity", "TA", "Temperature", "fCO2", "pCO2", "pHT"
    ]
    available_scenarios = [
        "historical", "ssp119", "ssp126", "ssp245", "ssp370", "ssp585"
    ]

    for var in variables:
        if var not in available_variables:
            raise ValueError(f"{var} not recognized. Choose from: {available_variables}")
    for scen in scenarios:
        if scen not in available_scenarios:
            raise ValueError(f"{scen} not recognized. Choose from: {available_scenarios}")

    variable_name_map = {
        "Temperature": "temperature"
        # add more mappings here if needed
    }

    base_url = "https://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0259391/nc/median/"
    output = {}

    for var in variables:
        output[var] = {}
        for scen in scenarios:
            filename = f"{var}_median_{scen}.nc"
            url = f"{base_url}{filename}"
            try:
                print(f"Downloading {filename}…")
                ds = xr.open_dataset(pooch_load(url, filename))
            except ReadTimeout:
                print(f"Download timed out, trying OSF mirror for {filename}…")
                osf_link_id = "ac7zg"
                mirror_url = f"https://osf.io/download/{osf_link_id}/"
                ds = xr.open_dataset(pooch_load(mirror_url, filename))

            actual_var_name = variable_name_map.get(var, var)
            output[var][scen] = ds[actual_var_name]

    return output