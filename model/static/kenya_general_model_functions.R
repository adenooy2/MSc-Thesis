assignTB_HIV=function(params_t,pop){

  pop$tb_status="tb_negative"
  pop$tb_present=0
  
  #HIV+ and PTB
  condHIVPTB=params_t$prev[params_t$tb_value_type=="ptb" & params_t$hiv==1]
  pop$tb_status[pop$hiv==1 & pop$rnum<condHIVPTB]="ptb"
  pop$tb_present[pop$hiv==1 & pop$rnum<condHIVPTB]=1
  
  #HIV+ and PTB
  condHIVEPTB=params_t$prev[params_t$tb_value_type=="eptb" & params_t$hiv==1]
  pop$tb_status[pop$hiv==1 & pop$rnum>=condHIVPTB & pop$rnum<(condHIVEPTB+condHIVPTB)]="eptb"
  pop$tb_present[pop$hiv==1 & pop$rnum>=condHIVPTB & pop$rnum<(condHIVEPTB+condHIVPTB)]=1
  
  #HIV+ and EPTB
  condHIVPTB=params_t$prev[params_t$tb_value_type=="ptb" & params_t$hiv==0]
  pop$tb_status[pop$hiv==0 & pop$rnum<condHIVPTB]="ptb"
  pop$tb_present[pop$hiv==0 & pop$rnum<condHIVPTB]=1
  
  #HIV+ and PTB
  condHIVEPTB=params_t$prev[params_t$tb_value_type=="eptb" & params_t$hiv==0]
  pop$tb_status[pop$hiv==0 & pop$rnum>=condHIVPTB & pop$rnum<(condHIVEPTB+condHIVPTB)]="eptb"
  pop$tb_present[pop$hiv==0 & pop$rnum>=condHIVPTB & pop$rnum<(condHIVEPTB+condHIVPTB)]=1
  
  #rif status
  rif_val=params_t$propRifRes[1]
  pop$rif_status=0
  pop$rnum=runif(n)
  pop$rif_status[pop$tb_present==1&pop$rnum<rif_val]=1
  
  return(pop)
}

assign_rif=function(group,group_size,currentParams){
  
  #rif status
  group$rif_status=0
  group$rif_status[group$tb_present==1&group$rnum<currentParams$propRifRes]=1
  
  return(group)
}

seek_care=function(group,group_size,currentParams){
  group$num_visits=0
  group$patient_time=0
  group$tb_seek_care=0
  
  group$rnum=runif(group_size)
  group$tb_seek_care[group$rnum<currentParams$p_visit]=1
  group$num_visits[group$tb_seek_care==1]=group$num_visits[group$tb_seek_care==1]+1
  group$patient_time[group$tb_seek_care==1]=group$patient_time[group$tb_seek_care==1]+currentParams$time_seek_care
  
  return(group)
}

screen_module=function(group,group_size,screenFlag,currentParams){
  group$do_triage=0
  group$tb_screened=0
  group$sens_screen=currentParams$sens_screen
  group$spec_screen=currentParams$spec_screen
  if(screenFlag==0){
    group$do_triage=1
    group$screen_result=NA
  }else{
    group$rnum=runif(group_size)
    group$tb_screened[group$tb_seek_care==1 & group$rnum<currentParams$p_screen]=1
    group$tb_screen_result=0
    
    #do screening
    group$rnum=runif(group_size)
    group$tb_screen_result[group$tb_screened==1 & group$tb_present==1 &group$rnum<currentParams$sens_screen]=1 #has TB
    group$tb_screen_result[group$tb_screened==1 & group$tb_present==0 &group$rnum>=currentParams$spec_screen]=1 #no TB
    group$patient_time[group$tb_screened==1]=group$patient_time[group$tb_screened==1]+currentParams$time_screen
    
    #not screened
    group$tb_screen_result[group$tb_screened==0 & group$tb_present==0]=NA #noscreen
    
    #set whether to do triage
    group$do_triage[ group$tb_screen_result==1]=1
  }
  
  return(group)
}


#Triage module
triage_module=function(group,group_size,triageFlag,currentParams){
  group$do_confirmatory=0
  group$tb_triaged=0
  group$sens_triage=currentParams$sens_triage
  group$spec_triage=currentParams$spec_triage
  
  if(triageFlag==0){
    
    group$do_confirmatory[group$do_triage==1]=1
    group$tb_triage_result=NA
    
  }else{48
    group$rnum=runif(group_size)
    group$tb_triaged[group$do_triage==1 & group$tb_seek_care==1 & group$rnum<currentParams$p_triage]=1
    group$tb_triage_result=0
    
    #do triage
    group$rnum=runif(group_size)
    group$tb_triage_result[group$tb_triaged==1 & group$tb_present==1 &group$rnum<currentParams$sens_triage]=1 #has TB
    group$tb_triage_result[group$tb_triaged==1 & group$tb_present==0 &group$rnum>=currentParams$spec_triage]=1 #no TB
    
    group$tb_triage_result[group$tb_triaged==0]=NA #no TB
    #Add time triage
    #group$patient_time[group$tb_triaged==1]=group$patient_time[group$tb_triaged==1]+currentParams$time_triage
    
    
    #set whether to do confirmatory
    group$do_confirmatory[ group$tb_triage_result==1]=1
  }
  
  return(group)
}

#offer testing
offered_testing=function(group,group_size,currentParams){
  group$tb_confirmatory_offered=0
  group$rnum=runif(group_size)
  group$tb_confirmatory_offered[group$do_confirmatory==1& group$tb_seek_care==1 & group$rnum<currentParams$p_test_offered]=1
  group$patient_time[group$tb_confirmatory_offered==1]=group$patient_time[group$tb_confirmatory_offered==1]+currentParams$time_offer_confirmatory
  return(group)
  }

#Sample collections
patient_referral=function(group,group_size,currentParams){
  group$patient_referred_for_sample=0
  group$patient_reached_sample_site=0
  
  group$rnum=runif(group_size)
  
  #patients referred
  group$patient_referred_for_sample[group$tb_confirmatory_offered==1& group$rnum<currentParams$p_patient_referral]=1
  group$rnum=runif(group_size)
  group$patient_reached_sample_site[group$patient_referred_for_sample==1& group$rnum<currentParams$p_visit]=1
  group$num_visits[group$patient_reached_sample_site==1 &group$patient_referred_for_sample==1] =group$num_visits[group$patient_reached_sample_site==1 &group$patient_referred_for_sample==1]+1
  group$patient_time[group$patient_reached_sample_site==1 &group$patient_referred_for_sample==1]=group$patient_time[group$patient_reached_sample_site==1 &group$patient_referred_for_sample==1]+currentParams$time_site_referral_visit
  
  #Patients not referred
  group$patient_reached_sample_site[group$tb_confirmatory_offered==1&group$patient_referred_for_sample==0]=1
  
  
  return(group)
}

set_diagnostic=function(group,group_size,currentParams){
  group$rnum=runif(group_size)
  group$conf_test="none"
  group$spec_conf=0
  group$sens_conf=0
  group$rif_sens=currentParams$sens_rif_external
  group$rif_spec=currentParams$spec_rif_external
  
  #which diagnostic is used
  group$conf_test[group$patient_reached_sample_site==1 & group$rnum<currentParams$p_xpert]="xpert"
  group$conf_test[group$patient_reached_sample_site==1 & group$rnum>=currentParams$p_xpert &group$rnum<(currentParams$p_xpert+currentParams$p_smear) ]="smear"
  group$conf_test[group$patient_reached_sample_site==1 & group$rnum>=(currentParams$p_xpert+currentParams$p_smear)]="other"
  
  #set sensitivity and specificity for xpert
  group$sens_conf[group$conf_test=="xpert"]=currentParams$sens_xpert
  group$spec_conf[group$conf_test=="xpert"]=currentParams$spec_xpert
  group$rif_sens[group$conf_test=="xpert"]=currentParams$sens_rif_xpert
  group$rif_spec[group$conf_test=="xpert"]=currentParams$spec_rif_xpert
  
  #set sensitivity and specificity for smear
  group$sens_conf[group$conf_test=="smear"]=currentParams$sens_smear
  group$spec_conf[group$conf_test=="smear"]=currentParams$spec_smear
  
  #set sensitivity and specificity for other
  group$sens_conf[group$conf_test=="other"]=currentParams$sens_other
  group$spec_conf[group$conf_test=="other"]=currentParams$spec_other
  
  
  return(group)
  
}

sample_provision=function(group,group_size,currentParams){
  group$conf_sample_provided=0
  group$conf_initial_sample_provided=0
  group$conf_sample_status=0
  
  group$rnum=runif(group_size)
  
  #Sample initially provided
  group$conf_initial_sample_provided[group$patient_reached_sample_site==1 & group$rnum>=currentParams$p_no_sample]=1
  group$conf_sample_provided[group$conf_initial_sample_provided==1]=1
  group$conf_sample_status[group$conf_initial_sample_provided==1]=1
  
  #sample not inittialy provided
  group$rnum=runif(group_size)
  group$conf_sample_provided[group$patient_reached_sample_site==1 & group$conf_initial_sample_provided==0  & group$rnum<currentParams$p_visit]=1
  group$conf_sample_status[group$conf_initial_sample_provided==0  & group$conf_sample_provided==1]=2
  group$num_visits[group$conf_sample_status==2 ] =group$num_visits[group$conf_sample_status==2 ]+1
  group$patient_time[group$conf_sample_status==2 ]=group$patient_time[group$conf_sample_status==2 ]+currentParams$time_new_sample_visit
  
  
  return(group)
}

#sample referral 
sample_referral=function(group, group_size,currentParams){
  
  group$rnum=runif(group_size)
  group$conf_sample_tested=0
  group$conf_sample_referred=0
  
  #sample referred and tested
  group$conf_sample_referred[group$conf_sample_provided==1 & group$rnum<currentParams$p_sample_referral]=1
  group$rnum=runif(group_size)
  group$conf_sample_tested[group$conf_sample_referred==1 & group$rnum<currentParams$p_sample_lab]=1
  
  #sample not referred and tested
  group$conf_sample_tested[group$conf_sample_referred==0 & group$conf_sample_provided==1]=1
  
  #tetsing time
  group$patient_time[group$conf_sample_tested==1 ]=group$patient_time[group$conf_sample_tested==1 ]+currentParams$time_sample_testing
  
  
  return(group)
}

#tesing sample with deisgnated diagnostic
sample_testing=function(group, group_size,currentParams){

  group$conf_sample_result=0
  group$rnum=runif(group_size)

  #Perform test
  group$conf_sample_result[group$conf_sample_tested==1 & group$tb_present==1 &group$rnum<group$sens_conf]=1 #has TB
  group$conf_sample_result[group$conf_sample_tested==1 & group$tb_present==0 &group$rnum>=group$spec_conf]=1 #no TB
  
  #NA for those not tested
  group$conf_sample_result[group$conf_sample_tested==0]=NA
  return(group)
  }

#Patient return to collect results
patient_result_collect=function(group, group_size, currentParams){
  
  group$patient_conf_result_received=NA
  
  #result same encounter
  group$rnum=runif(group_size)
  group$conf_res_same_encounter=0
  group$conf_res_same_encounter[group$conf_sample_tested==1 & group$rnum<currentParams$p_encounter_res]=1
  group$patient_conf_result_received[group$conf_res_same_encounter==1]=group$conf_sample_result[group$conf_res_same_encounter==1]
  
  #result different encounter
  group$rnum=runif(group_size)
  group$patient_conf_result_received[group$conf_sample_tested==1 & group$conf_res_same_encounter==0 & group$rnum<currentParams$p_return_results]=group$conf_sample_result[group$conf_sample_tested==1 & group$conf_res_same_encounter==0 & group$rnum<currentParams$p_return_results]
  
  #add patient time and visit for those receiving results in different encounter
  group$num_visits[is.na(group$patient_conf_result_received)==FALSE & group$conf_res_same_encounter==0 ] =group$num_visits[is.na(group$patient_conf_result_received)==FALSE & group$conf_res_same_encounter==0  ]+1
  group$patient_time[is.na(group$patient_conf_result_received)==FALSE & group$conf_res_same_encounter==0  ]=group$patient_time[is.na(group$patient_conf_result_received)==FALSE & group$conf_res_same_encounter==0  ]+currentParams$time_collect_result
  
  
  return(group)
}


empiric_notification=function(group, group_size, currentParams){
  
  group$emp_notification=0
  group$rnum=runif(group_size)
  
  group$emp_notification[group$patient_conf_result_received==0 & group$rnum<currentParams$p_emp]=1
  group$patient_conf_result_received[group$emp_notification==1]=1
  
  return(group)
}



confirmatory_module=function(group,group_size,currentParams){
  
  #Offered testing
  group=offered_testing(group,group_size,currentParams)
  
  #sample collection
  group=patient_referral(group,group_size,currentParams)
  
  #set diagnostic
  group=set_diagnostic(group,group_size,currentParams)
  
  #sample provision
  group=sample_provision(group,group_size,currentParams)
  
  #sample referral
  group=sample_referral(group, group_size,currentParams)
  
  #sample testing
  group=sample_testing(group, group_size,currentParams)
  
  #result collection
  group=patient_result_collect(group, group_size, currentParams)
  
  #emppriric result
  group=empiric_notification(group, group_size, currentParams)
  
  return(group)
}


access_rif=function(group,group_size,currentParams){
  group$rif_included=0
  group$rif_tested=0
  group$rif_offsite=1
  
  
  #is rif included in the diagnostic
  group$rnum=runif(group_size)
  group$rif_included[is.na(group$patient_conf_result_received)==FALSE & group$rnum<=currentParams$p_rif_included]=1
  group$rif_tested[is.na(group$patient_conf_result_received)==FALSE & group$rnum<=currentParams$p_rif_included]=1
  
  # rif not included - rif testing onsite
  group$rnum=runif(group_size)
  group$rif_tested[is.na(group$patient_conf_result_received)==FALSE &group$rif_included==0 & group$rnum<=currentParams$p_rif_onsite]=1
  group$rif_offsite[group$rif_tested==1]=0
  
  # rif not included - rif testing offsite
  group$rnum=runif(group_size)
  group$num_visits[is.na(group$patient_conf_result_received)==FALSE & group$rif_tested==0 & group$rnum<=currentParams$p_visit_rif] =group$num_visits[is.na(group$patient_conf_result_received)==FALSE & group$rif_tested==0 & group$rnum<=currentParams$p_visit_rif  ]+1
  group$patient_time[is.na(group$patient_conf_result_received)==FALSE & group$rif_tested==0 & group$rnum<=currentParams$p_visit_rif ]=group$patient_time[is.na(group$patient_conf_result_received)==FALSE & group$rif_tested==0 & group$rnum<=currentParams$p_visit_rif ]+currentParams$time_rif_visit
  group$rif_tested[is.na(group$patient_conf_result_received)==FALSE &group$rif_tested==0 & group$rnum<=currentParams$p_visit_rif]=1
  
  
  return(group)
}

rif_testing=function(group,group_size,currentParams){
 
  group$rif_lab_result=0
  group$rnum=runif(group_size)
  
  #Perform test
  group$rif_lab_result[group$rif_tested==1 & group$rif_status==1 &group$rnum<group$rif_sens]=1 #has TB
  group$rif_lab_result[group$rif_tested==1 & group$rif_status==0 &group$rnum>=group$rif_spec]=1 #no TB
  
  #NA for those not tested
  group$rif_lab_result[group$rif_tested==0]=NA
  return(group)
}

#rif result collection
rif_result_collection=function(group,group_size, currentParams){
 
  group$patient_rif_result_received=NA
  
  #result same encounter
  group$rnum=runif(group_size)
  group$rif_same_encounter=0
  group$rif_same_encounter[group$rif_tested==1 & group$rnum<=currentParams$p_encounter_res_rif]=1
  group$patient_rif_result_received[group$rif_same_encounter==1]=group$rif_lab_result[group$rif_same_encounter==1]
  
  #result different encounter
  group$rnum=runif(group_size)
  group$patient_rif_result_received[group$rif_tested==1 & group$rif_same_encounter==0 & group$rnum<currentParams$p_return_rif_res]=group$rif_lab_result[group$rif_tested==1 & group$rif_same_encounter==0 & group$rnum<currentParams$p_return_rif_res]
  
  #add patient time and visit for those receiving results in different encounter
  group$num_visits[is.na(group$patient_rif_result_received)==FALSE & group$rif_same_encounter==0 ] =group$num_visits[is.na(group$patient_rif_result_received)==FALSE & group$rif_same_encounter==0  ]+1
  group$patient_time[is.na(group$patient_rif_result_received)==FALSE & group$rif_same_encounter==0  ]=group$patient_time[is.na(group$patient_rif_result_received)==FALSE & group$rif_same_encounter==0  ]+currentParams$time_collect_rif_results
  
  
  
  return(group)
}
  
  
#Rif module
rif_module=function(group,group_size,currentParams){
  #access rif
  group=access_rif(group,group_size,currentParams)
  
  #rif testing
  group=rif_testing(group,group_size,currentParams)
  
  #rif collection
  group=rif_result_collection(group,group_size, currentParams)
  
  return(group)
}
  
  
#Run cascade for a group
run_group_cascade=function(group,currentParams,screenFlag,triageFlag){
  group_size=nrow(group)
  
  #seek care
  group=seek_care(group,group_size,currentParams)
  
  #screening
  group=screen_module(group,group_size,screenFlag,currentParams)
  
  #triage
  group=triage_module(group,group_size,triageFlag,currentParams)
  
  #confirmatory
  group=confirmatory_module(group,group_size,currentParams)
  
  #rif
  #group=rif_module(group,group_size,currentParams)
}
  
  
#sumilate full population
simulate_population=function(pop,params_t){
  #sure there is a better wya to do this but my brain is giving out on me
  
  ## group runs
  #HIV pos eptb
  hiv_pos_eptb=pop %>% filter(hiv==1&tb_status=="eptb")
  hiv_pos_eptb_params=params_t %>% filter(hiv==1&tb_value_type=="eptb")
  hiv_pos_eptb=run_group_cascade(hiv_pos_eptb,hiv_pos_eptb_params,screenFlag,triageFlag)
  #HIV pos PTB or no TB
  hiv_pos_ptb_notb=pop %>% filter(hiv==1&tb_status!="eptb")
  hiv_pos_ptb_notb_params=params_t %>% filter(hiv==1&tb_value_type!="eptb")
  hiv_pos_ptb_notb=run_group_cascade(hiv_pos_ptb_notb,hiv_pos_ptb_notb_params,screenFlag,triageFlag)
  #HIV neg PTB eptb
  hiv_neg_eptb=pop %>% filter(hiv==0&tb_status=="eptb")
  hiv_neg_eptb_params=params_t %>% filter(hiv==0&tb_value_type=="eptb")
  hiv_neg_eptb=run_group_cascade(hiv_neg_eptb,hiv_neg_eptb_params,screenFlag,triageFlag)
  #HIV neg PTB or no TB
  hiv_neg_ptb_notb=pop %>% filter(hiv==0&tb_status!="eptb")
  hiv_neg_ptb_notb_params=params_t %>% filter(hiv==0&tb_value_type!="eptb")
  hiv_neg_ptb_notb=run_group_cascade(hiv_neg_ptb_notb,hiv_neg_ptb_notb_params,screenFlag,triageFlag)
  
  #simulate population
  sim_pop=rbind(hiv_pos_eptb,hiv_pos_ptb_notb) %>% rbind(hiv_neg_eptb) %>% rbind(hiv_neg_ptb_notb)
  
  return(sim_pop)
}
  
  
