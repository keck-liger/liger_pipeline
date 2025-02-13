from .model_base import TMTDataModel

__all__ = ['IRISCubeModel']


class IRISCubeModel(TMTDataModel):
    """
    A data model for 3D image cubes.

    Parameters
    __________
    data : numpy float32 array
         The science data

    dq : numpy uint32 array
         Data quality array

    err : numpy float32 array
         Error array

    zeroframe : numpy float32 array
         Zero frame array

    area : numpy float32 array
         Pixel area map array

    int_times : numpy table
         table of times for each integration

    wavelength : numpy float32 array
         Wavelength array

    var_poisson : numpy float32 array
         Integration-specific variances of slope due to Poisson noise

    var_rnoise : numpy float32 array
         Integration-specific variances of slope due to read noise
    """
    schema_url = "iris_cube.schema.yaml"

    def __init__(self, init=None, **kwargs):

        super().__init__(init=init, **kwargs)

        # Implicitly create arrays
        self.dq = self.dq
        self.err = self.err

    def to_container(self):
        """Convert to a ModelContainer of ImageModels for each plane"""
        from .datamodels import IRISImageModel, ModelContainer
        from jwst.datamodels import ModelContainer

        container = ModelContainer()
        for plane in range(self.shape[0]):
            image = IRISImageModel()
            for attribute in [
                    'data', 'dq', 'err', 'zeroframe', 'area',
                    'var_poisson', 'var_rnoise', 'var_flat'
            ]:
                try:
                    setattr(image, attribute, self.getarray_noinit(attribute)[plane])
                except AttributeError:
                    pass
            image.update(self)
            try:
                image.meta.wcs = self.meta.wcs
            except AttributeError:
                pass
            container.append(image)
        return container
