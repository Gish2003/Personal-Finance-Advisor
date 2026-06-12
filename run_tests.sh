#!/usr/bin/env bash
# Run all PLUnit test suites for the Personal Finance Advisor.
set -e

cd "$(dirname "$0")"

swipl -g "
consult('prolog/tests/test_calculations.pl'),
consult('prolog/tests/test_foo_rules.pl'),
consult('prolog/tests/test_recommendations.pl'),
consult('prolog/tests/test_scenarios.pl'),
run_tests,
halt" -t "halt(1)"
