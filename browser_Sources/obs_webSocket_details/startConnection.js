const obs = new OBSWebSocket();
      wsConnect();

      async function wsConnect() 
      {  
          await connectOBS(obs);
        }