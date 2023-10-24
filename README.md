# Sales-Lead-Qualifier Project (AMOS WS 2023/24)

![Screenshot 2023-10-24 at 19 48 33](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/assets/45459787/003c9302-760f-4ca7-8c7a-12be99886715)

## Branching Strategy  

**main**: It contains fully stable production code
* **dev**: It contains stable under-development code
    
  * **epic**: It contains a module branch. Like high level of feature. For example, we have an authentication module then we can create a branch like "epic/authentication"

    * **feature**: It contains specific features under the module. For example, under authentication, we have a feature called registration. Sample branch name: "feature/registration"

    * **bugfix**: It contains bug fixing during the testing phase and  branch name start with the issue number for example "bugfix/3-validate-for-wrong-user-name"
