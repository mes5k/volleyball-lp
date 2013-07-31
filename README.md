volleyball-lp
=============

A volleyball league schedule mixed integer linear program generator.

This project consists of a single python script which is used to generate
a mixed integer linear program used for scheduling a volleyball league.
The output of the program is a text file formatted in the "lp" format
of [lp_solve](http://lpsolve.sourceforge.net/). You will need to run
lp_solve with the generated file to produce a schedule.
