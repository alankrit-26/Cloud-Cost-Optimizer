#include<bits/stdc++.h>
using namespace std;


class GoogleDocs{
    private:
    vector<string>text;    
    vector<string>path;
    public:
     
    void addText(string sx){
        text.push_back(sx);
    }

    void addPath(string s1){
        text.push_back(s1);
    }

    string renderDocument(){
        string ans="";
        for(auto it:text){
            if(it.size()>4 && (it.substr(it.size()-3)==".jpg" || it.substr(it.size()-3)=="png")){
                ans+="Image: "+it+"\n";
            }
            else{
                ans+=it+"\n";
            }
        }
        return ans;
    }

};
int main(){
    GoogleDocs* pt=new GoogleDocs();
    pt->addText("HELLO WORLD!");
    pt->addPath("document is the key");
    pt->addText("asfjdhbadfwaefji");
    pt->addPath("htiawN Rkwermxwer.png");
    cout<<pt->renderDocument();
}