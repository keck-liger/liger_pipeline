import logging
import importlib
from gwcs.wcs import WCS
from astropy.modeling import models
from astropy import coordinates as coord
from astropy import units as u
from gwcs import coordinate_frames as cf

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__all__ = ["load_wcs"]


def load_wcs(input_model, reference_files={}):
    """
    Create a gWCS object and store it in ``Model.meta``.

    Parameters
    ----------
    input_model : `~jwst.datamodels.DataModel`
        The exposure.
    reference_files : dict
        A dict {reftype: reference_file_name} containing all
        reference files that apply to this exposure.
    """

    if "wcsinfo" not in input_model.meta:
        input_model.meta.cal_step.assign_wcs = "SKIPPED"
        log.warning("assign_wcs: SKIPPED")
        return input_model
    else:
        output_model = input_model.copy()
        shift_by_crpix = models.Shift(
            -(input_model.meta.wcsinfo.crpix1 - 1) * u.pix
        ) & models.Shift(-(input_model.meta.wcsinfo.crpix2 - 1) * u.pix)
        pix2sky = getattr(
            models, "Pix2Sky_{}".format(input_model.meta.wcsinfo.ctype1[-3:])
        )()
        celestial_rotation = models.RotateNative2Celestial(
            input_model.meta.wcsinfo.crval1 * u.deg,
            input_model.meta.wcsinfo.crval2 * u.deg,
            180 * u.deg,
        )
        pix2sky.input_units_equivalencies = {
            "x": u.pixel_scale(input_model.meta.wcsinfo.cdelt1 * u.deg / u.pix),
            "y": u.pixel_scale(input_model.meta.wcsinfo.cdelt2 * u.deg / u.pix),
        }
        det2sky = shift_by_crpix | pix2sky | celestial_rotation
        det2sky.name = "linear_transform"
        detector_frame = cf.Frame2D(
            name="detector", axes_names=("x", "y"), unit=(u.pix, u.pix)
        )
        sky_frame = cf.CelestialFrame(
            reference_frame=getattr(
                coord, input_model.meta.coordinates.reference_frame
            )(),
            name="sky_frame",
            unit=(u.deg, u.deg),
        )
        pipeline = [(detector_frame, det2sky), (sky_frame, None)]

        wcs = WCS(pipeline)
        output_model.meta.wcs = wcs
        output_model.meta.cal_step.assign_wcs = "COMPLETE"
    return output_model
