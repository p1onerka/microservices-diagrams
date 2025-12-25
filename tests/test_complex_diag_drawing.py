from diag_drawer import build_diag_mermaid

def test_complex_diagram_building():
    diag = build_diag_mermaid("tests/test_query_data")
    expected = '''graph LR
classDef discovery_server fill:#79eaec,stroke:#55b8b9,stroke-width:2px;
classDef eureka_client fill:#8ae692,stroke:#55b95e,stroke-width:2px;
classDef config_server fill:#d8a059,stroke:#956e3d,stroke-width:2px;
discovery-server[discovery-server]:::discovery_server
admin-server[admin-server]:::eureka_client
api-gateway[api-gateway]:::eureka_client
customers-service[customers-service]:::eureka_client
genai-service[genai-service]:::eureka_client
vets-service[vets-service]:::eureka_client
visits-service[visits-service]:::eureka_client
subgraph LEGEND["configs for all services"]
direction LR

spring-petclinic-config-server[spring-petclinic-config-server]:::config_server
spring-petclinic-config-server["<a href=https://github.com/spring-petclinic/spring-petclinic-microservices-config>spring-petclinic-config-server</a>"];
end
admin-server -->|register| discovery-server
linkStyle 0 stroke:#117a1a,stroke-width:5px;
api-gateway -->|register| discovery-server
linkStyle 1 stroke:#117a1a,stroke-width:5px;
customers-service -->|register| discovery-server
linkStyle 2 stroke:#117a1a,stroke-width:5px;
genai-service -->|register| discovery-server
linkStyle 3 stroke:#117a1a,stroke-width:5px;
vets-service -->|register| discovery-server
linkStyle 4 stroke:#117a1a,stroke-width:5px;
visits-service -->|register| discovery-server
linkStyle 5 stroke:#117a1a,stroke-width:5px;
api-gateway -->|http requests from 
pet-form.controller.js| customers-service
linkStyle 6 stroke:#4a4599,stroke-width:5px;
api-gateway -->|http requests from 
chat.js| genai-service
linkStyle 7 stroke:#4a4599,stroke-width:5px;
api-gateway -->|http requests from 
vet-list.controller.js| vets-service
linkStyle 8 stroke:#4a4599,stroke-width:5px;
api-gateway -->|http requests from 
visits.controller.js| visits-service
linkStyle 9 stroke:#4a4599,stroke-width:5px;
api-gateway -->|get apps instances| discovery-server
linkStyle 10 stroke:#74d9,stroke-width:5px;
api-gateway -->|http requests from 
CustomersServiceClient.java| customers-service
linkStyle 11 stroke:#4a4599,stroke-width:5px;
api-gateway -->|http requests from 
VisitsServiceClient.java| visits-service
linkStyle 12 stroke:#4a4599,stroke-width:5px;
genai-service -->|http requests from 
AIDataProvider.java| customers-service
linkStyle 13 stroke:#4a4599,stroke-width:5px;
genai-service -->|http requests from 
VectorStoreController.java| vets-service
linkStyle 14 stroke:#4a4599,stroke-width:5px;'''
    assert diag == expected