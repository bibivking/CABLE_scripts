#!/usr/bin/env python

"""
Run CABLE spatially.

This script sets various things within a qsub script and then submits the run.

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (27.07.2018)"
__email__ = "mdekauwe@gmail.com"

import subprocess
import sys
import os
import glob
import shutil
import tempfile
import optparse
from adjust_namelist_files import adjust_nml_file

class RunCable(object):

    def __init__(self, met_path, log_dir, output_dir, aux_dir,
                 yearly_namelist_dir, soil_fname, veg_fname, co2_fname,
                 grid_fname, mask_fname, nml_fname, qsub_template_fname):

        self.met_path = met_path
        self.log_dir = log_dir
        self.output_dir = output_dir
        self.aux_dir = aux_dir
        self.veg_dir = os.path.join(self.aux_dir, "core/biogeophys")
        self.grid_dir = os.path.join(self.aux_dir, "offline")
        self.soil_fname = soil_fname
        self.veg_fname = os.path.join(self.aux_dir, veg_fname)
        self.soil_fname = os.path.join(self.aux_dir, soil_fname)
        self.grid_fname = os.path.join(self.grid_dir, grid_fname)
        self.mask_fname = os.path.join(self.aux_dir,
                                       "offline/%s" % (mask_fname))
        self.yearly_namelist_dir = yearly_namelist_dir
        self.nml_fname = nml_fname
        self.co2_fname = co2_fname
        self.grid_fname = grid_fname
        self.qsub_template_fname = qsub_template_fname

    def setup_nml_file(self):

        replace_dict = {
                        "filename%met": "'%s'" % (self.met_path),
                        "filename%type": "'%s'" % (self.grid_fname),
                        "filename%veg": "'%s'" % (self.veg_fname),
                        "filename%soil": "'%s'" % (self.soil_fname),
                        "gswpfile%mask": "'%s'" % (self.mask_fname),
                        "output%averaging": "'monthly'",
                        "spinup": ".FALSE.",
        }
        adjust_nml_file(self.nml_fname, replace_dict)


    def run_me(self, start_yr, end_yr):

        qs_cmd = 'qsub -v start_yr=%d,end_yr=%d %s' % \
                    (start_yr, end_yr, self.qsub_template_fname)
        print(qs_cmd)
        error = subprocess.call(qs_cmd, shell=True)
        if error is 1:
            print("Job failed to submit")
            sys.exit()

    def create_new_nml_file(self, log_fname, out_fname, restart_in_fname,
                            restart_out_fname, year, co2_conc):

        out_log_fname = os.path.join(self.log_dir, log_fname)
        out_fname = os.path.join(self.output_dir, out_fname)
        restart_in_fname = os.path.join(self.restart_dir, restart_in_fname)
        restart_out_fname = os.path.join(self.restart_dir, restart_out_fname)

        replace_dict = {
                        "filename%log": "'%s'" % (out_log_fname),
                        "filename%out": "'%s'" % (out_fname),
                        "filename%restart_in_fname": "'%s'" % (restart_in_fname),
                        "filename%restart_out_fname": "'%s'" % (restart_out_fname),
                        "fixedCO2": "%d" % (co2_conc),
                        "gswpfile%rainf": "/gswp/Rainf/GSWP3.BC.Rainf.3hrMap.%s.nc" % (year),
                        "gswpfile%snowf": "/gswp/Snowf/GSWP3.BC.Snowf.3hrMap.%s.nc" % (year),
                        "gswpfile%LWdown": "/gswp/LWdown/GSWP3.BC.LWdown.3hrMap.%s.nc" % (year),
                        "gswpfile%SWdown": "/gswp/SWdown/GSWP3.BC.SWdown.3hrMap.%s.nc" % (year),
                        "gswpfile%PSurf": "/gswp/PSurf/GSWP3.BC.PSurf.3hrMap.%s.nc" % (year),
                        "gswpfile%Qair": "/gswp/Qair/GSWP3.BC.Qair.3hrMap.%s.nc" % (year),
                        "gswpfile%Tair": "/gswp/Tair/GSWP3.BC.Tair.3hrMap.%s.nc" % (year),
                        "gswpfile%wind": "/gswp/Wind/GSWP3.BC.Wind.3hrMap.%s.nc" % (year),

        }
        adjust_nml_file(self.nml_fname, replace_dict)

        # save copy as we go for debugging - remove later
        shutil.copyfile("site.nml", os.path.join(self.yearly_namelist_dir,
                                                 "site_%d_year.nml" % (year)))

def cmd_line_parser():

    p = optparse.OptionParser()
    p.add_option('--person', '-p', default="world")
    p.add_option("-s", action="store_true", default=False,
                   help="Setup namelist file")
    p.add_option("-a", action="store_true", default=False,
                   help="Adjust namelist file")
    p.add_option("-y", default="0", help="year")
    p.add_option("-l", default="", help="log filename")
    p.add_option("-o", default="", help="out filename")
    p.add_option("-i", default="", help="restart in filename")
    p.add_option("-r", default="", help="restart out filename")
    p.add_option("-c", default="400.0", help="CO2 concentration")

    return p.parse_args()

if __name__ == "__main__":

    #------------- Change stuff ------------- #
    met_path = "/g/data1/wd9/MetForcing/Global/GSWP3_2017/"
    log_dir = "logs"
    aux_dir = "/g/data1/w35/mrd561/CABLE/CABLE_AUX-dev/"
    output_dir = "outputs"
    restart_dir = "restarts"
    yearly_namelist_dir = "backup_namelists" # remove later
    co2_fname = "Annual_CO2_concentration_until_2010.txt"
    grid_fname = "CABLE_UNSW_GSWP3_gridinfo_0.5x0.5.nc"
    mask_fname = "gswp3_landmask_nomissing.nc"
    soil_fname = "def_soil_params.txt"
    veg_fname = "def_veg_params_zr_clitt_albedo_fix.txt"
    nml_fname = "cable.nml"
    qsub_template_fname = "qsub_scripts/run_cable_spatial_template.sh"
    start_yr = 1950
    end_yr = 1951
    # ------------------------------------------- #

    if not os.path.exists(restart_dir):
        os.makedirs(restart_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if not os.path.exists(yearly_namelist_dir):
        os.makedirs(yearly_namelist_dir)

    options, args = cmd_line_parser()

    C = RunCable(met_path, log_dir, output_dir, aux_dir, yearly_namelist_dir,
                 soil_fname, veg_fname, co2_fname, grid_fname, mask_fname,
                 nml_fname, qsub_template_fname)

    # qsub script is adjusting namelist file
    if options.a:
        log_fname = options.l
        out_fname = options.o
        restart_in_fname = options.i
        restart_out_fname = options.r
        year = int(options.yr)
        co2_conc = int(options.c)
        print(out_fname)
        C.create_new_nml_file(log_fname, out_fname, restart_in_fname,
                              restart_out_fname, year, co2_conc)

    # Setup initial namelist file and submit qsub job
    else:
        shutil.copyfile(os.path.join(aux_dir, "offline/%s" % (nml_fname)),
                        nml_fname)
        C.setup_nml_file()
        C.run_me(start_yr, end_yr)
