import math

from schemas import PvtRequest, PvtResponse


def __convert_temperature_in_kelvin_to_fahrenheit(t_kel: float) -> float:
    return 1.8 * (t_kel - 273.15) + 32


def __convert_gas_content_in_m3_m3_to_foot_barrel(r_s: float) -> float:
    return r_s / 0.17810760667903522


def __convert_gamma_oil_in_fraction_to_degrees_api(gamma_oil: float) -> float:
    return (145.5 / gamma_oil) - 135.5


def __calculate_v_oil(v_liq: float, wct: float) -> float:
    return v_liq * (1 - wct)


def __calculate_v_gas(v_oil: float, gor: float) -> float:
    return v_oil * gor


def __calculate_gf(v_gas: float, v_liq: float) -> float:
    return v_gas / (v_liq + v_gas)


def __calculate_b_g(t_kel: float, p: float) -> float:
    return 350.958 * (t_kel / p)


def __calculate_ro_gas(gamma_gas: float, b_g: float) -> float:
    return (28.97 * gamma_gas) / (24.04220577350111 * b_g)


def __calculate_r_s(
    gamma_gas: float, gamma_oil: float, t_kel: float, p: float
) -> float:
    y_g = 1.2254503 + 0.001638 * t_kel - (1.76875 / gamma_oil)
    return (
        gamma_gas
        * (1.9243101395421235 * 10 ** (-6) * (p / 10**y_g)) ** 1.2048192771084338
    )


def __calculate_b_oil(
    gamma_gas: float, gamma_oil: float, r_s: float, t_kel: float
) -> float:
    return (
        0.972
        + (147 / 10**6)
        * (5.61458 * r_s * (gamma_gas / gamma_oil) ** 0.5 + 2.25 * t_kel - 574.5875)
        ** 1.175
    )


def __calculate_ro_oil(
    gamma_gas: float, gamma_oil: float, r_s: float, b_oil: float
) -> float:
    return 1000 * ((gamma_oil + (1.2217 / 1000) * r_s * gamma_gas) / b_oil)


def __calculate_ro_liq(ro_oil: float, wct: float) -> float:
    return ro_oil * (1 - wct) + 1000 * wct


def __calculate_ro_mix(ro_liq: float, ro_gas: float, gf: float) -> float:
    return ro_liq * (1 - gf) + ro_gas * gf


def __calculate_mu_gas(gamma_gas: float, ro_gas: float, t_kel: float) -> float:
    b = 2.57 + (1914.5 / (1.8 * t_kel)) + 0.275 * gamma_gas
    mu_gas = (
        10 ** (-4)
        * (7.77 + 0.183 * gamma_gas)
        * ((1.8 * t_kel) ** 1.5 / (122.4 + 373.6 * gamma_gas + 1.8 * t_kel))
        * math.exp(b * (ro_gas / 1000) ** (1.11 + 0.04 * b))
    )
    return mu_gas


def __calculate_mu_oil_dead(t_far: float, gamma_oil: float) -> float:
    d = t_far ** (-1.163) * 10 ** (3.0324 - 0.02023 * gamma_oil)
    mu_oil_dead = 10**d - 1
    return mu_oil_dead


def __calculate_mu_oil(r_s: float, t_far: float, gamma_oil: float) -> float:
    if t_far > 70:
        mu_dead = __calculate_mu_oil_dead(t_far=t_far, gamma_oil=gamma_oil)
        mu_oil = (
            10.715
            * (r_s + 100) ** (-0.515)
            * mu_dead ** (5.44 * (r_s + 150) ** (-0.338))
        )
    else:
        d_70 = 70 ** (-1.163) * 10 ** (3.0324 - 0.02023 * gamma_oil)
        d_80 = 80 ** (-1.163) * 10 ** (3.0324 - 0.02023 * gamma_oil)
        mu_oil_80 = 10**d_80 - 1
        mu_oil_70 = 10**d_70 - 1
        l_78 = math.log10((80 / 70))
        l_mu = math.log10((mu_oil_70 / mu_oil_80))
        c = l_mu / l_78
        b = 70**c * mu_oil_70
        d = math.log10(b) - c * math.log10(t_far)

        mu_oil = 10**d
    return mu_oil


def __calculate_mu_liq(wct: float, gamma_oil: float, r_s: float, t_far: float) -> float:
    mu_oil = __calculate_mu_oil(r_s=r_s, t_far=t_far, gamma_oil=gamma_oil)
    mu_liq = mu_oil * (1 - wct) + wct
    return mu_liq


def __calculate_mu_mix(
    gf: float,
    gamma_gas: float,
    gamma_oil: float,
    ro_gas: float,
    wct: float,
    t_kel: float,
    r_s: float,
) -> float:
    t_far = __convert_temperature_in_kelvin_to_fahrenheit(t_kel=t_kel)
    r_s = __convert_gas_content_in_m3_m3_to_foot_barrel(r_s=r_s)
    gamma_oil = __convert_gamma_oil_in_fraction_to_degrees_api(gamma_oil=gamma_oil)

    mu_gas = __calculate_mu_gas(gamma_gas=gamma_gas, ro_gas=ro_gas, t_kel=t_kel)
    mu_liq = __calculate_mu_liq(wct=wct, gamma_oil=gamma_oil, r_s=r_s, t_far=t_far)

    mu_mix = mu_liq * (1 - gf) + mu_gas * gf
    return mu_mix


def __calculate_v_mix(v_liq: float, v_gas: float) -> float:
    return v_liq + v_gas


async def calculate_pvt_data(
    pvt_data: PvtRequest,
) -> PvtResponse:
    # Расчет вспомогательных данных, которые будут переиспользоваться
    v_oil = __calculate_v_oil(v_liq=pvt_data.QLiq, wct=pvt_data.Wct)
    v_gas = __calculate_v_gas(v_oil=v_oil, gor=pvt_data.Rp)
    gf = __calculate_gf(v_gas=v_gas, v_liq=pvt_data.QLiq)

    b_g = __calculate_b_g(
        t_kel=pvt_data.T, p=pvt_data.P
    )
    ro_gas = __calculate_ro_gas(gamma_gas=pvt_data.GammaGas, b_g=b_g)

    r_s = __calculate_r_s(
        gamma_gas=pvt_data.GammaGas,
        gamma_oil=pvt_data.GammaOil,
        t_kel=pvt_data.T,
        p=pvt_data.P,
    )
    b_oil = __calculate_b_oil(
        gamma_gas=pvt_data.GammaGas,
        gamma_oil=pvt_data.GammaOil,
        r_s=r_s,
        t_kel=pvt_data.T,
    )
    ro_oil = __calculate_ro_oil(
        gamma_gas=pvt_data.GammaGas,
        gamma_oil=pvt_data.GammaOil,
        r_s=r_s,
        b_oil=b_oil,
    )
    ro_liq = __calculate_ro_liq(ro_oil=ro_oil, wct=pvt_data.Wct)

    # Расчет основных данных
    ro_mix = __calculate_ro_mix(ro_liq=ro_liq, ro_gas=ro_gas, gf=gf)
    mu_mix = __calculate_mu_mix(
        gf=gf,
        gamma_gas=pvt_data.GammaGas,
        gamma_oil=pvt_data.GammaOil,
        ro_gas=ro_gas,
        wct=pvt_data.Wct,
        t_kel=pvt_data.T,
        r_s=r_s,
    )
    v_mix = __calculate_v_mix(v_liq=pvt_data.QLiq, v_gas=v_gas)

    res_data = {
        "QMix": v_mix,
        "RhoMix": ro_mix,
        "MuMix": mu_mix,
    }
    res_data = PvtResponse(**res_data)
    return res_data
