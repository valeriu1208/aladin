Para ejecutar el codigo de manera exitosa, hemos implmentado ngrok, este ngrok se ejecuta de la siguiente manera(previamente hay que instalarlo)
ngrok http 8501, lo usamos porque al tener el google authenticator, la redirección que hace no es segura, y al usar ngrok crea un tipo
de "capa" intermedia para las solicitudes que la hace segura.
Además, para poder realizar las conexiones "invisibles" con las API's, hay un fichero dentro de .streamlit que es secrets.toml, allí se encuentran todos las Key's que no deben ser visibles para el usuario.
Cualquier duda, mailto:valeriu.marian.moldovan@estudiantat.upc.edu
