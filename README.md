# Desenvolvimento de um modelo híbrido de comunicação

Cronograma - Entregas

1- Definição da aplicação para testes do modelo de comunicação;
2- Testes de desempenho da aplicação no modelo de comunicação atual;
3- Desenvolvimento do novo modelo de comunicação do PIS;
4- Testes de desempenho do novo modelo e comparações;
5- Inserção do novo modelo de comunicação do PIS;
6- Entrega da versão final, defesa e versão final.

## Aplicação para testes

A aplicação definida para ser usada nos testes do modelo de comunicação e validação do novo modelo é a [is-person-detector](https://github.com/JoabFelippx/is-person-detector), essa aplicação recebe imagens vindas dos gateways das câmeras, faz a detectção de pessoas e publica em tópicos específicos, para que sejam consumidas e usadas conform necessário. 

## Testes de desempenho da aplicação no modelo atual

Foi usada a aplicação [is-commtrace-exporter](https://github.com/labviros/is-commtrace-exporter) para coletar os dados referentes ao tempo de comunicação entre os Gateway das câmeras e a aplicação. A aplicação is-person-detector foi modificada para que fosse possível medir o tempo de comunicação.

Pendências:

Colocar o broker em um local geograficamente distante e coletar os dados.

## Desenvolvimento do modelo

1- Pub-sub imagens normal com o broker, coletando tempo de comunicação.
2- Comunicação entre o produtor da imagem e o consumidor com UDP, coletando tempo de comunicação.
