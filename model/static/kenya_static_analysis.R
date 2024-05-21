rm(list=ls())
library(tidyverse)
library(readxl)
library(ggplot2)
library(stringr)
options(scipen=999)

#Split files by scenario
fileSetScen=function(pathScenarios){
  #Path to model data
  path=pathScenarios
  files=list.files(path)
  
  #Collect names of all files
  fileDF=data.frame(files)
  
  #split file names into dtrings
  fileDFSplit=data.frame(t(data.frame((str_split(fileDF$files,"_")))))
  fileDFSplit$file=fileDF$files
  fileDF$files=gsub('\\[',"",fileDF$files)
  fileDF$files=gsub(']',"",fileDF$files)
  
  #select the country, prevalencem scenario, run and shortened filename of each file
  fileDFSplit=fileDFSplit %>% select(X1,X3,file)
  colnames(fileDFSplit)=c("scenario","run","filename")
  fileDFSplit$run=as.numeric(gsub(".xlsx","",fileDFSplit$run))
  fileDFSplit$label=fileDFSplit$scenario
  
  #Generate a list of unique labels (label indiciates which runs should be averaged together)
  fileGroups=fileDFSplit %>% select(scenario) %>% unique()
  fileGroups$label=paste(fileGroups$scenario)
  fileDFSplit$filename=gsub("~","",fileDFSplit$filename)
  fileDFSplit$filename=gsub("$","",fileDFSplit$filename)
  
  return(list(fileGroups,fileDFSplit))
}

simulationCounts=function(results){
  #tbCohort
  simCountsTB=results %>% filter(tb_present==1) %>% select(tb_present, tb_seek_care,tb_confirmatory_offered,conf_sample_provided,
                                                           ,patient_conf_result_received)
  
  #Count pathway points
  path_countsTB=data.frame(colSums(simCountsTB,na.rm=TRUE))
  colnames(path_countsTB)[1]="count"
  path_countsTB$variable=rownames(path_countsTB)
  path_countsTB=path_countsTB %>% spread(variable,count)

  
  return(path_countsTB)
  
}


cascadeCounts=function(results){
 # Count all columns with no NA
  cascadeData=results %>% select(tb_seek_care,tb_confirmatory_offered,patient_reached_sample_site,
                                   conf_sample_provided, conf_sample_tested )
  
  #Count pathway points
  cascadeCounts=data.frame(colSums(cascadeData,na.rm=TRUE))
  colnames(cascadeCounts)[1]="count"
  cascadeCounts$variable=rownames(cascadeCounts)
  cascadeCounts=cascadeCounts %>% spread(variable,count)
  
  cascadeCounts$total_individuals=nrow(results)
  cascadeCounts$all_patient_received_results=sum(is.na(results$patient_conf_result_received)==FALSE)
  colnames(cascadeCounts)=c("all_provide_sample","all_sample_tested","all_reach_sample_site","all_offered_testing","all_sought_care",
                            "all_individuals","all_patients_received_results")
  return(cascadeCounts)
  
}


aggregateFiles=function(fileGroups,fileDFSplit,path){
  finalOutcomes=data.frame()
  ######## Read file by file, summarise results by group
  for(k in 1:nrow(fileGroups))
  {
    #k=1
    #empty group dataframes
    simCounts=data.frame()
    casCounts=data.frame()
    fileList=fileDFSplit %>% filter(label==fileGroups$label[k]) #k
    
    #results per run
    for(i in 1:nrow(fileList))
    {
      #i=1
      results=read_excel(paste(path,fileList$filename[i],sep="")) #i
      tempSimCounts=simulationCounts(results)
      tempCascadeCounts=cascadeCounts(results)
      simCounts=rbind(simCounts,tempSimCounts)
      casCounts=rbind(casCounts,tempCascadeCounts)
    }
    
    
    #average sim counts
    avgSimCounts=data.frame(t(round(colMeans(simCounts),0)))
    avgSimCounts$case_detection=avgSimCounts$patient_conf_result_received/avgSimCounts$tb_present
    
    avgCasCounts=data.frame(t(round(colMeans(casCounts),0)))
    
    tempFinalOutcomes=cbind(avgSimCounts,avgCasCounts)
    tempFinalOutcomes$scenario=fileGroups$label[k]
    finalOutcomes=rbind(finalOutcomes,tempFinalOutcomes)
   
  }
  
  allData=finalOutcomes
  
  return(allData)
}




path="/Users/adenooy/Library/CloudStorage/OneDrive-Personal/UVA/Thesis/MSc-Thesis/data/static/output/"
scenarioFiles=fileSetScen(path)
fileGroups=scenarioFiles[[1]]
fileDFSplit=scenarioFiles[[2]]
scenarioData=aggregateFiles(scenarioFiles[[1]],scenarioFiles[[2]],path)

baseCascade=scenarioData %>% filter(scenario=="baseline") %>% select(tb_present, tb_seek_care,tb_confirmatory_offered,conf_sample_provided,
                                                                     ,patient_conf_result_received)

baseCascade=baseCascade %>% gather(variable,count)
baseCascade$perc=round(baseCascade$count/max(baseCascade$count)*100,1)

baseCascade$var_lab=c("Individuals with TB","Sought care","Offered testing","Provided sample","Received TB positive diagnosis")

temp=baseCascade %>% select(var_lab,variable)

#Plot tB cascade baseline
ggplot(baseCascade,aes(x=reorder(var_lab,-count),y=count,fill=variable))+
  geom_bar(stat="identity")+theme_bw()+xlab("Pathway Point")+ylab("Number of individuals")+
  labs(title="Percentage of individuals with TB reaching differents points in the patient diagnostic journey")+
  geom_text(aes(x=reorder(var_lab,-count),y=count+25,size=30,label=paste(perc,"%",sep="")))+
  theme(text = element_text(size=20))+theme(legend.position = "none")
#scale_x_discrete(guide = guide_axis(n.dodge=2))

#Plot scenario casacdes
scenarioDataWide=scenarioData %>% gather(variable,value,1:6) %>% 
  filter(variable!="case_detection") %>% 
  arrange(scenario,desc(value)) %>% group_by(scenario) %>% 
  mutate(max_scenario=max(value),perc=round(100*(value/max_scenario),0)) %>% 
  left_join(temp)


ggplot(scenarioDataWide,aes(x=reorder(var_lab,-value),y=value,fill=var_lab))+facet_wrap(.~scenario)+
  geom_bar(stat="identity",position="dodge")+theme_bw()+xlab("Pathway Point")+ylab("Number of individuals")+
  labs(title="Percentage of individuals with TB reaching differents points in the patient diagnostic journey")+
  geom_text(aes(x=reorder(var_lab,-value),y=value+25,size=30,label=paste(perc,"%",sep="")))+
  theme(text = element_text(size=16))+theme(legend.position = "none")+scale_x_discrete(guide = guide_axis(n.dodge=2))

#Export TB Scenario data
#write.csv(scenarioData,"/Users/adenooy/Library/CloudStorage/OneDrive-Personal/UVA/Thesis/MSc-Thesis/data/static/summary_scenario_results.csv")

#case detection plot
cdr_data=scenarioData %>% select(scenario,case_detection)
cdr_data$case_detection=round(100*cdr_data$case_detection,1)

ggplot(cdr_data,aes(scenario,case_detection,fill=case_detection))+geom_bar(stat="identity")+
  theme_bw()+xlab("Scenario")+ylab("Case Detection rate (%)")+
  labs(title="Case detection rates resulting from each scenario")+
  geom_text(data=cdr_data,aes(x=scenario,y=case_detection+3,label=paste(case_detection,"%",sep=""),size=20))+
  theme(text = element_text(size=20))+theme(legend.position = "none")+ scale_fill_gradient2(low='red', mid='orange', high='darkgreen',midpoint=65)

##Testing and results rate full cohort
fullCohort=scenarioData %>% select(scenario,all_individuals,all_sought_care,all_offered_testing,
                                   all_reach_sample_site,all_provide_sample,all_sample_tested,all_patients_received_results)

write.csv(fullCohort,"/Users/adenooy/Library/CloudStorage/OneDrive-Personal/UVA/Thesis/MSc-Thesis/data/static/full_cohort_results.csv")

