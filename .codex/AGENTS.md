# Instruções do repositório

## Arquivos de Perfil

Os arquivos `public/profile*.json` serão fontes canônicas de todo o histórico profissional da pessoa.


## Sobre Alterações em arquivos profile*.json

1. Sempre que uma alteração for feita, altere o `meta.version` e o `meta.last_updated` de acordo.
2. Se uma modificação for feita no arquivo de uma língua específica, valide a necessidade de alterar os arquivos `*.json` das demais línguas
3. Sempre que alterar qualquer arquivo em `public/profile*.json`, execute `python scripts/convert_profiles_to_toon.py` para atualizar os arquivos TOON correspondentes antes de concluir a tarefa.

## TOON FILES

Os arquivos `**/*.toon` são apenas para leitura e NUNCA devem ser modificados diretamente. Eles existem no projeto apenas para reduzirmos o consumo de tokens. 