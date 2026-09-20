# Agronomy advisory scope

The first advisory implementation provides conservative screening guidance for:

- Maize
- Rice
- Groundnuts
- Beans
- Millets
- Soybeans

The engine checks broad soil-pH and active-growth temperature ranges and
considers whether the crop is in a moisture-sensitive growth stage. It does
not provide fertilizer rates, pesticide recommendations, guaranteed yield
predictions, or a replacement for local agronomic advice.

## Required context

The advisory input should include:

- Farm location
- Crop
- Growth stage
- Soil pH
- Soil moisture
- Temperature
- Humidity

If location or growth stage is missing, the result is explicitly marked
conditional rather than being presented as site-specific advice.

## Reference basis

The screening ranges are informed by:

- [FAO-56 Crop evapotranspiration](https://www.fao.org/4/X0490E/X0490E00.htm)
- [FAO Irrigation Water Management](https://www.fao.org/4/s2022e/s2022e00.htm)
- [FAO Ecocrop](https://ecocrop.apps.fao.org/ecocrop/srv/en/home)
- [CIMMYT maize resources](https://www.cimmyt.org/maize/)
- [AfricaRice](https://www.africarice.org/)
- [ICRISAT](https://www.icrisat.org/)
- [Oklahoma State University peanut production guide](https://extension.okstate.edu/fact-sheets/peanut-production-guide.html)

These references describe ranges and management principles, not a universal
decision rule for every farm. Local soil tests, weather observations, cultivar
guidance, and extension recommendations remain authoritative.
