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

aggregateFiles=function(fileGroups,fileDFSplit,path){
  finalOutcomes=data.frame()
  ######## Read file by file, summarise results by group
  for(k in 1:nrow(fileGroups))
  {
    #k=1
    #empty group dataframes
    simCounts=data.frame()
    fileList=fileDFSplit %>% filter(label==fileGroups$label[k]) #k
    
    #results per run
    for(i in 1:nrow(fileList))
    {
      #i=1
      results=read_excel(paste(path,fileList$filename[i],sep="")) #i
      tempSimCounts=simulationCounts(results)
      simCounts=rbind(simCounts,tempSimCounts)
    }
    
    
    #average sim counts
    avgSimCounts=data.frame(t(round(colMeans(simCounts),0)))
    avgSimCounts$case_detection=avgSimCounts$patient_conf_result_received/avgSimCounts$tb_present
    
    tempFinalOutcomes=avgSimCounts
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

baseCascade=scenarioData %>% filter(scenario=="baseline")
baseCascade$scenario=NULL
baseCascade$case_detection=NULL
baseCascade=baseCascade %>% gather(variable,count)
baseCascade$perc=round(baseCascade$count/max(baseCascade$count)*100,1)

#Plot tB cascade baseline
ggplot(baseCascade,aes(x=reorder(variable,-count),y=count,fill=variable))+
  geom_bar(stat="identity")+theme_bw()+xlab("Pathway Point")+ylab("Number of individuals")+
  labs(title="Percentage of individuals with TB reaching differents points in the patient diagnostic journey")+
  geom_text(aes(x=reorder(variable,-count),y=count+25,size=30,label=paste(perc,"%",sep="")))+
  scale_x_discrete(guide = guide_axis(n.dodge=2))+theme(text = element_text(size=20))+theme(legend.position = "none")



