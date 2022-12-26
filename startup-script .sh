curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.2/install.sh | bash

export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

echo "INSERT_JSON_CREDENTIALS_TAKEN_FROM_GOOGLE" >> kkk.json
export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/kkk.json"

mkdir front
cd front

nvm install node

npm install express --save
npm install firebase-admin --save
npm install request --save



rm index.*

echo "const express = require('express')
const request = require('request');
const app = express()
const port = 8080

const { initializeApp, applicationDefault, cert } = require('firebase-admin/app');
const { getFirestore, Timestamp, FieldValue } = require('firebase-admin/firestore');

initializeApp({
  credential: applicationDefault()
});

const db = getFirestore();
const cateroriesRef = db.collection('categorized-gundem')

app.get('/', (req,res) => {
  res.sendFile(\`\${__dirname}/index.html\`)
})

app.get('/get', async (req, res) => {
  const cat = await cateroriesRef.get()
  const last = cat.docs.sort((doc1, doc2) => doc2.createTime.toMillis() - doc1.createTime.toMillis())
  res.json(last.at(0).data())
})

app.get('/trigger', async (req, res) => {
      request('https://us-central1-glowing-bird-367505.cloudfunctions.net/eksi-gundem');
})

app.listen(port, () => {})" >> index.js

echo "<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Document</title>
    <script src='https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js'></script>
</head>
<body>
    <div>
        <input id='input' type='number'>
    <button onclick='triggerCategorize()'>
        Send a trigger to start the categorization process
    </button>
    <button onclick='get()'>Get Latest Categorized Gundem</button>
    </div>
    <pre id='content'>

    </pre>
    

    <script>
        const inputNode = document.querySelector('#input');
        const triggerCategorize = () => {
            const data = inputNode.value
            console.log(data)
            axios.get(\`https://us-central1-glowing-bird-367505.cloudfunctions.net/eksi-gundem?page=\${data}\`).then((res)=>{
            console.log(res)
            }).catch((err)=>console.log(err))
        }
        const get = () => {
        
            axios.get('/get').then((res)=>{
            document.querySelector('#content').innerHTML = JSON.stringify(res.data, null, 2)
            }).catch((err)=>console.log(err))
        }
    </script>
</body>
</html>" >> index.html



node index.js & 