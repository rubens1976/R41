document.querySelector("#btn-buscar").addEventListener("click", function(e) {
    e.preventDefault();
    
    var tribunal = document.querySelector("#tribunal").value;
    var codigoTPU = document.querySelector("#codigo_tpu").value;
    
    // Ação de enviar para o backend ou realizar outra lógica
    fetch(`/buscar-processos/?tribunal=${tribunal}&codigo_tpu=${codigoTPU}`)
        .then(response => response.json())
        .then(data => {
            console.log(data); // Acompanhe a resposta
            // Processar os dados recebidos aqui, talvez exibir no frontend
        })
        .catch(error => console.error("Erro:", error));
});
