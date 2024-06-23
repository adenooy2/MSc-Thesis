## Optimising TB diagnostic Implementation in Kenya

This repository hold the code, models and outputs for this thesis project. The project is focused on determining the optimal combination of TB diagnostics in Kenya, given different implementation  considerations. These include the test being used, where testing is occuring, the sample-type and how quickly results are returned. In the project two analyses were conducted, each using a different model. The first took the form of a patient pathway analysis (a static analysis) - which determined for a group of people with TB the estimated case detection rate for diffeerent implementation scenarios. The second analysis used a transmission model (dynamic analysis) to predict the long-term effect of each scenario on the TB epidemic.

### Research Question
To what extent do different implementations of molecular testing change TB case detection rates and what impact do they have on the TB epidemic over time, as compared to the current standard of care for tuberculosis diagnosis in Kenya?

Further sub-research questions include:
  - To what extent do different scenarios of diagnostic implementation change the percentage of individuals being correctly diagnosed with TB?
  - Which implementation scenarios have the greatest impact on the percentage of of individuals being tested for TB?
  - Which implementation scenarios have the greatest impact on increasing the number of individuals receiving TB results?
  - To what extent do different diagnostic implementations impact the number of new TB cases and TB deaths over time?

### File structure
In the repository there are several key folders:
  - Data: Contains the input data for both models as well as the output from the static analysis
  - Documentation: Contaings key documents, data write-ups and drafts of the project
  - Model: Contains the original unadapted patient pathway for kenya, the newly developed generalisable patient pathway model and the files needed for the transmission model

