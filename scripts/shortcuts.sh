#!/bin/bash
using() {
	envcmd="env AGC_CONF=conf_$1.yaml"
	shift
	actual_cmd="$@"
	$envcmd $actual_cmd
}