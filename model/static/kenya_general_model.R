rm(list=ls())
source("/Users/adenooy/Library/CloudStorage/OneDrive-Personal/UVA/Thesis/MSc-Thesis/model/static/kenya_general_model_functions.R")
library(tidyverse)
library(readxl)
library(ggplot2)
library(stringr)
library(openxlsx)
options(scipen=999)

#Do time triage

#Run Options
n=10000
runs=20
basePath="/Users/adenooy/Library/CloudStorage/OneDrive-Personal/UVA/Thesis/MSc-Thesis/"

scenarios=c("baseline","scenario1","scenario2","scenario3")

for(j in 1:length(scenarios)){
  scen=scenarios[j]  

#Parameters
params=read_excel(paste(basePath,"data/static/input/parameters.xlsx",sep=""),sheet=scen)
params_t= data.frame(t(params[-1]))
colnames(params_t)=params$variable
params_t$hiv=c(0,1,0,1)
params_t$tb_value_type=c("ptb","ptb","eptb","eptb")


for (i in 1:runs){
 

#Assign HIV and TB status for the population
hiv=rbinom(n,1,params_t$propHIV[1])
pop=data.frame(hiv)
pop$rnum=runif(n)
pop=assignTB_HIV(params_t,pop)

#scenario Options
screenFlag=0
triageFlag=0

#simulate scenario
sim_pop=simulate_population(pop,params_t)

write.xlsx(sim_pop, paste(basePath,"data/static/output/",scen,"_","run_",i,".xlsx",sep=""))
}

}

# scenario analysis -------------------------------------------------------
temp=sim_pop %>% filter(tb_present==1) %>% filter(patient_conf_result_received==1)

#sumamry of those with TB
tb_results=temp %>% summarise(tb_total=sum(tb_present),seek_care=sum(tb_seek_care),
                                                           screened=sum(tb_screened),
                                                           triaged=sum(tb_triaged),
                                                           offered_confirmatory=sum(tb_confirmatory_offered),
                                                           reach_sample_site=sum(patient_reached_sample_site),
                                                           sample_provided=sum(conf_sample_provided),
                                                           conf_sample_tested=sum(conf_sample_tested),
                                                           total_visits=sum(num_visits))

