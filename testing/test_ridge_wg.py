import pylum
import pylum.structure.waveguide as wg
import pylum.fdemode as fde
import pylum.structure.ridge_wg as ridge
wg = wg.Waveguide(3e-6,3e-6,1.2e-6)
environ = ridge.RidgeWaveguideEnvironment(wg, False)
fde = fde.FDEModeSimulator(environ)
fde.setup_sim(1.2e-6)