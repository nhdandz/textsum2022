#!/bin/bash
screen -SX clustering quit 
screen -SX clustering2 quit 
screen -SX root_kafka quit 
screen -SX multi_kafka quit 
screen -SX algo_control quit 
screen -SX texrank quit 
screen -SX multexrank quit 
screen -SX multexrank quit 
screen -XS textsum_fe quit
screen -XS textsum_be quit