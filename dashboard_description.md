## Descrição da Página Principal (Dashboard)

A página principal (Dashboard) do sistema Templo Digital, baseada no template `dashboard/index.html`, apresenta as seguintes seções e componentes:

1.  **Cabeçalho Padrão:**
    *   Herdado do template `core/base.html`.
    *   Título da página: "Dashboard".
    *   Barra de pesquisa.
    *   Ícones de atualização e notificações.
    *   Informações do usuário logado (nome e avatar).

2.  **Cartões de Estatísticas (Topo):**
    *   Uma grade com quatro cartões destacados, cada um com uma borda colorida à esquerda e um ícone correspondente:
        *   **Total de Membros:** Fundo branco, borda azul, ícone de pessoas. Exibe o número total de membros cadastrados e um link para a lista de membros.
        *   **Total de Igrejas:** Fundo branco, borda roxa, ícone de igreja. Exibe o número total de igrejas cadastradas e um link para a lista de igrejas.
        *   **Eventos do Mês:** Fundo branco, borda verde, ícone de calendário. Exibe o número de eventos agendados para o mês atual e um link para a lista de eventos.
        *   **Arrecadação Mensal:** Fundo branco, borda amarela, ícone de moeda. Exibe o valor total arrecadado no mês atual e um link para a seção de finanças.

3.  **Próximos Eventos:**
    *   Uma seção com o título "Próximos Eventos".
    *   Uma tabela listando os eventos futuros mais próximos.
    *   Colunas da tabela: Título (com link para detalhes), Data, Hora, Igreja e Tipo (com formatação colorida baseada no tipo).
    *   Um link "Ver todos →" para acessar a lista completa de eventos.
    *   Caso não haja eventos próximos, uma mensagem informativa é exibida.

4.  **Gráficos e Estatísticas (Inferior):**
    *   Uma grade com duas seções reservadas para gráficos:
        *   **Membros por Igreja:** Placeholder para um gráfico que mostra a distribuição de membros por igreja.
        *   **Resumo Financeiro:** Placeholder para um gráfico que resume as entradas e saídas financeiras.
    *   *Observação: Os gráficos em si não estão implementados no template atual, apenas os placeholders.*

5.  **Barra Lateral Padrão:**
    *   Herdada do template `core/base.html`.
    *   Links para todas as seções do sistema (Dashboard, Igrejas, Membros, Eventos, Finanças, Escola, Usuários - se admin).
    *   O link "Dashboard" estará visualmente destacado como ativo.
    *   Links para "Meu Perfil" e "Sair".

6.  **Rodapé Padrão:**
    *   Herdado do template `core/base.html`.
    *   Texto de copyright "Templo Digital © [Ano Atual] - Sistema de Gestão para Igrejas".

Em resumo, o dashboard oferece uma visão geral rápida das informações mais importantes do sistema, como contagem de membros e igrejas, eventos próximos e um resumo financeiro, além de fornecer acesso rápido às principais seções através dos cartões e da barra lateral.
