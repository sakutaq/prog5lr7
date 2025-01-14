document.addEventListener('DOMContentLoaded', () => {
  const clientIdDiv = document.getElementById('client-id');
  const currencyDataDiv = document.getElementById('currency-data');

    const socket = io();

     socket.on('connect', () => {
        console.log('WebSocket connection opened.');
    });

    socket.on('client_id', (data) => {
       console.log('Client ID received.')
       if(data && data.client_id){
         clientIdDiv.textContent = `Client ID: ${data.client_id}`;
       }

   });


  socket.on('currency_update', (data) => {
       console.log('Currency update received.')
       if (data && data.currency_data) {
          currencyDataDiv.textContent = JSON.stringify(data.currency_data, null, 2); // форматирование
      }
  });

    socket.on('disconnect', () => {
    console.log('WebSocket connection closed.');
     });

});
