# Sales-Lead-Qualifier Project (AMOS WS 2023/24)

## Sum Insight Logo

![team-logo-white-1280x720](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/assets/45459787/7d38795e-6bd5-4003-9b23-29911532b0f8)
![team-logo-black-1280x720](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/assets/45459787/a7314df0-1917-4384-8f6c-2ab9f9831047)


## Branching Strategy  

**main**: It contains fully stable production code
* **dev**: It contains stable under-development code
    
  * **epic**: It contains a module branch. Like high level of feature. For example, we have an authentication module then we can create a branch like "epic/authentication"

    * **feature**: It contains specific features under the module. For example, under authentication, we have a feature called registration. Sample branch name: "feature/registration"

    * **bugfix**: It contains bug fixing during the testing phase and  branch name start with the issue number for example "bugfix/3-validate-for-wrong-user-name"
