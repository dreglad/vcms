Cómo instalar y usar esta aplicación
====================================

Instalación
--

**Clonar repositorio**

        git clone https://bitbucket.org/news-hub/video.git
        cd video

**Crear, correr y aprovisionar máquina virtual**

        vagrant up


Accesos
--

Credenciales por defecto:  *admin/admin*


**Backend**

        http://127.0.0.1:8080/admin/


**Administrador de Videos**

        http://127.0.0.1:8080/admin-videos/


**API v1**

        http://127.0.0.1:8080/api/v1/

Documentación: http://pub.docs.openmultimedia.biz/servicios/api-rest-multimedia


**API v2**

        http://127.0.0.1:8080/api/v2/

En su mayoría auto-documentada


**Endpoint de operaciones**
        
        POST http://127.0.0.1:8080/ops/crear_nuevo
        POST http://127.0.0.1:8080/ops/query_nuevo
        POST http://127.0.0.1:8080/ops/editar_clip
        POST http://127.0.0.1:8080/ops/publicar_clip
        POST http://127.0.0.1:8080/ops/despublicar_clip
        POST http://127.0.0.1:8080/ops/eliminar_clip