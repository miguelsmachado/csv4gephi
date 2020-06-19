import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64

def get_table_download_link(df):

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href


def main():
    st.title("CSV 4 Gephi")
    st.markdown("Faça o upload do seu arquivo csv para que os dados sejam preparados para serem utlizados pelo Gephi.")
    st.markdown("Caso tenha alguma dúvida de como gerar esse arquivo, consulte o tutorial do "
                "[Projeto](https://bit.ly/3dy0AQ1)")
    st.markdown("___")
    st.header("**Atenção**")
    st.subheader("Colunas mínimas")
    st.text("O arquivo baixado do Facepager, deve conter ao menos as seguintes colunas:")
    min_col = pd.DataFrame({'colunas':['user.screen_name', 'entities.user_mentions.0.screen_name', 'object_id',
                 'created_at', 'text', 'retweeted_status.retweet_count', 'user.location']})
    st.dataframe(min_col.colunas)

    st.subheader("Separador")
    radio = st.radio("Antes de fazer o upload, escolha o separador:", ("Ponto-e-vírgula ( ; )", "Vírgula ( , )"))
    if radio == "Ponto-e-vírgula ( ; )":
        separador = ';'
    if radio == "Vírgula ( , )":
        separador = ','

    st.header("Upload do arquivo")
    file = st.file_uploader('Escolha a base de dados que deseja preparar (.csv)', type='csv')
    if file is not None:
        df = pd.read_csv(file, sep=separador)
        # Realizando ajuste inicial

        # Filtrando as colunas necessárias
        df = df[['user.screen_name', 'entities.user_mentions.0.screen_name', 'object_id',
                 'created_at', 'text', 'retweeted_status.retweet_count', 'user.location']]

        # Alterando o nome das colunas
        df.columns = ['source', 'target', 'object_id', 'created_at', 'tweet_text',
                      'retweet_count', 'user.location']
        # Criando a culuna url
        df['url'] = 'https://twitter.com/' + df['target'] + '/status/' + df['object_id']

        df.dropna(inplace=True)
        df_original = df.copy()
        min_tw = st.slider('Escolha o numero mínimo de retwites:', min_value=0, max_value=200)
        bt_filtro = st.button("Filtrar")
        bt_desfazer_filtro = st.button("Desfazer Filtro")
        if bt_filtro:
            selecao = df.retweet_count >= int(min_tw)
            df = df[selecao]
        if bt_desfazer_filtro:
            df = df_original.copy()

        # Exibição
        number = st.slider('Escolha o numero de linhas que deseja visualizar:', min_value=1, max_value=100, value=10)
        st.dataframe(df.head(number))

        st.markdown("___")
        st.header("Otimizando os parâmetros de busca")

        df_research = df[['target', 'tweet_text']]
        # eliminando dados duplicados, pois precisamos de apenas uma mensagem de cada.
        df_research = df_research.drop_duplicates()
        # separando as palavras
        words = df_research
        words["tweet_text"] = df_research["tweet_text"].str.lower()
        words = words["tweet_text"].str.get_dummies(" ").sum().sort_values(ascending=False)
        # Badwords
        bad_words = ['rt', 'de', 'e', 'o', 'a', 'em', 'na', 'no', 'de', 'da', 'com',
                     'como', 'é', 'do', 'os', 'ou', "que", "não", 'para', 'por', 'mais',
                     'um', 'uma', 'ao', 'as', 'se', 'dos', 'nas', 'pela', 'pra',
                     'das'
                     ]

        add_bad_words = st.text_input("Digite as palavras que deseja excluir separadas espaço")
        bt_add_bad_words = st.button("Exluir palavras")
        if bt_add_bad_words:
            bad_words.extend(str(add_bad_words).split(" "))

        top_words = words.drop(labels=bad_words)

        # Exibição topwords
        number1 = st.slider('Escolha o numero de linhas que deseja visualizar:', min_value=1, max_value=100, value=20)
        st.dataframe(top_words.head(number1))

        st.markdown("___")
        st.header("Top Hashtags")

        # criando as novas variáveis que serão utilizadas
        df_hashtags = df_research
        df_hashtags['tweet_text'] = df_research['tweet_text'].str.split()
        hashtags = []
        mentions = []

        # buscando por '#' e '@'
        for text in df_hashtags.tweet_text:
            for palavra in text:
                if '#' in palavra:
                    hashtags.append(palavra)
                elif '@' in palavra:
                    mentions.append(palavra)

        # criando as Series com as top# e top@
        top_mentions = pd.Series(mentions).str.get_dummies(':').sum().sort_values(ascending=False)
        top_hashtags = pd.Series(hashtags).str.get_dummies(' ').sum().sort_values(ascending=False)

        # Exibindo as top hashtags
        number2 = st.slider('Selecione o número de #:', min_value=1, max_value=50, value=10)
        st.dataframe(top_hashtags.head(number2))

        bt_wordcloud_hashtags = st.button("Gerar Wordcloud", key='hashtags')
        if bt_wordcloud_hashtags:
            # criando um texto com todas as hashtags
            all_hashtags = " ".join(s for s in hashtags)
            # criando a wordcloud
            wordcloud = WordCloud(background_color="black",
                                  width=1600, height=800).generate(all_hashtags)
            fig, ax = plt.subplots(figsize=(15, 9))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.set_axis_off()
            plt.imshow(wordcloud)
            st.pyplot()

        st.markdown("___")
        st.header("Top Mentions")
        number3 = st.slider('Escolha o número de @:', min_value=1, max_value=50, value=10)
        st.dataframe(top_mentions.head(number3))

        bt_wordcloud_hashtags = st.button("Gerar Wordcloud")
        if bt_wordcloud_hashtags:
            # criando um texto com todas as menções
            all_mentions = " ".join(s for s in mentions)
            # criando a wordcloud
            wordcloud = WordCloud(background_color="black",
                                  width=1600, height=800).generate(all_mentions)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.set_axis_off()
            plt.imshow(wordcloud)
            st.pyplot()

        st.markdown("___")
        st.header("Maiores Influenciadores")
        st.subheader("São os usuários que foram mais retwitados")

        graph_retweet = df.groupby('target')['target'].count().sort_values(ascending=False).head(15)
        st.dataframe(graph_retweet)

        bt_graf_infl = st.button("Gerar Gráfico")
        if bt_graf_infl:

            plt.figure(figsize=(16, 8))
            sns.set_style("whitegrid")
            plt.xticks(rotation=45)


            sns.barplot(x=graph_retweet.index,
                        y=graph_retweet.values,
                        palette=sns.color_palette("BuGn_r", n_colors=len(graph_retweet.index))).set_title(
                "TOP INFLUENCIADORES")
            st.pyplot()

        st.markdown("___")
        st.header("Maiores Twittadores")
        st.subheader("São os usuários que postaram sobre o assunto")

        graph_retweet_1 = df_research.groupby('target')['target'].count().sort_values(ascending=False).head(15)
        st.dataframe(graph_retweet_1)

        bt_graf_twi = st.button("Gerar Gráfico", key='a')
        if bt_graf_twi:
            plt.figure(figsize=(16, 8))
            sns.set_style("whitegrid")
            plt.xticks(rotation=45)

            sns.barplot(x=graph_retweet_1.index,
                        y=graph_retweet_1.values,
                        palette=sns.color_palette("BuGn_r", n_colors=len(graph_retweet_1.index))).set_title(
                "TOP TWITTADORES")
            st.pyplot()

        st.markdown("___")
        st.header("Encontrando a localização dos usuários:")

        df_loc = pd.read_csv("municipios.csv")
        df_municipios = df_loc[['nome', 'codigo_uf']]
        df_user_loc = df['user.location']

        ro = df_municipios.query("codigo_uf==11")['nome'].str.lower()
        ac = df_municipios.query("codigo_uf==12")['nome'].str.lower()
        am = df_municipios.query("codigo_uf==13")['nome'].str.lower()
        rr = df_municipios.query("codigo_uf==14")['nome'].str.lower()
        pa = df_municipios.query("codigo_uf==15")['nome'].str.lower()
        ap = df_municipios.query("codigo_uf==16")['nome'].str.lower()
        to = df_municipios.query("codigo_uf==17")['nome'].str.lower()
        ma = df_municipios.query("codigo_uf==21")['nome'].str.lower()
        pi = df_municipios.query("codigo_uf==22")['nome'].str.lower()
        ce = df_municipios.query("codigo_uf==23")['nome'].str.lower()
        rn = df_municipios.query("codigo_uf==24")['nome'].str.lower()
        pb = df_municipios.query("codigo_uf==25")['nome'].str.lower()
        pe = df_municipios.query("codigo_uf==26")['nome'].str.lower()
        al = df_municipios.query("codigo_uf==27")['nome'].str.lower()
        se = df_municipios.query("codigo_uf==28")['nome'].str.lower()
        ba = df_municipios.query("codigo_uf==29")['nome'].str.lower()
        mg = df_municipios.query("codigo_uf==31")['nome'].str.lower()
        es = df_municipios.query("codigo_uf==32")['nome'].str.lower()
        rj = df_municipios.query("codigo_uf==33")['nome'].str.lower()
        sp = df_municipios.query("codigo_uf==35")['nome'].str.lower()
        pr = df_municipios.query("codigo_uf==41")['nome'].str.lower()
        sc = df_municipios.query("codigo_uf==42")['nome'].str.lower()
        rs = df_municipios.query("codigo_uf==43")['nome'].str.lower()
        ms = df_municipios.query("codigo_uf==50")['nome'].str.lower()
        mt = df_municipios.query("codigo_uf==51")['nome'].str.lower()
        go = df_municipios.query("codigo_uf==52")['nome'].str.lower()
        df1 = df_municipios.query("codigo_uf==53")['nome'].str.lower()

        contador_de_cidades = {'ro': 0, 'ac': 0, 'am': 0, 'rr': 0, 'pa': 0, 'ap': 0, 'to': 0,
                               'ma': 0, 'pi': 0, 'ce': 0, 'rn': 0, 'pb': 0, 'pe': 0, 'al': 0,
                               'se': 0, 'ba': 0, 'mg': 0, 'es': 0, 'rj': 0, 'sp': 0, 'pr': 0,
                               'sc': 0, 'rs': 0, 'ms': 0, 'mt': 0, 'go': 0, 'df1': 0
                               }

        # criando uma lista para armazenar os dados que não forem encontrados
        nao_encontradas = []

        for linha in df_user_loc.values:
            for cidade in linha.lower().split(','):
                if cidade.strip() in ro.values:
                    contador_de_cidades['ro'] += 1
                    break
                elif cidade.strip() in ac.values:
                    contador_de_cidades['ac'] += 1
                    break
                elif cidade.strip() in am.values:
                    contador_de_cidades['am'] += 1
                    break
                elif cidade.strip() in rr.values:
                    contador_de_cidades['rr'] += 1
                    break
                elif cidade.strip() in pa.values:
                    contador_de_cidades['pa'] += 1
                    break
                elif cidade.strip() in ap.values:
                    contador_de_cidades['ap'] += 1
                    break
                elif cidade.strip() in to.values:
                    contador_de_cidades['to'] += 1
                    break
                elif cidade.strip() in ma.values:
                    contador_de_cidades['ma'] += 1
                    break
                elif cidade.strip() in pi.values:
                    contador_de_cidades['pi'] += 1
                    break
                elif cidade.strip() in ce.values:
                    contador_de_cidades['ce'] += 1
                    break
                elif cidade.strip() in rn.values:
                    contador_de_cidades['rn'] += 1
                    break
                elif cidade.strip() in pb.values:
                    contador_de_cidades['pb'] += 1
                    break
                elif cidade.strip() in pe.values:
                    contador_de_cidades['pe'] += 1
                    break
                elif cidade.strip() in al.values:
                    contador_de_cidades['al'] += 1
                    break
                elif cidade.strip() in se.values:
                    contador_de_cidades['se'] += 1
                    break
                elif cidade.strip() in ba.values:
                    contador_de_cidades['ba'] += 1
                    break
                elif cidade.strip() in mg.values:
                    contador_de_cidades['mg'] += 1
                    break
                elif cidade.strip() in es.values:
                    contador_de_cidades['es'] += 1
                    break
                elif cidade.strip() in rj.values:
                    contador_de_cidades['rj'] += 1
                    break
                elif cidade.strip() in sp.values:
                    contador_de_cidades['sp'] += 1
                    break
                elif cidade.strip() in pr.values:
                    contador_de_cidades['pr'] += 1
                    break
                elif cidade.strip() in sc.values:
                    contador_de_cidades['sc'] += 1
                    break
                elif cidade.strip() in rs.values:
                    contador_de_cidades['rs'] += 1
                    break
                elif cidade.strip() in ms.values:
                    contador_de_cidades['ms'] += 1
                    break
                elif cidade.strip() in mt.values:
                    contador_de_cidades['mt'] += 1
                    break
                elif cidade.strip() in go.values:
                    contador_de_cidades['go'] += 1
                    break
                elif cidade.strip() in df1.values:
                    contador_de_cidades['df1'] += 1
                    break
                else:
                    nao_encontradas.append(cidade.strip())

        #Exibindo dataframe
        loc_user = pd.Series(contador_de_cidades).sort_values(ascending=False)
        st.dataframe(loc_user)

        bt_mostra_graf_users = st.button("Exibir Gráfico")
        if bt_mostra_graf_users:
            grafico = pd.Series(data=contador_de_cidades).sort_values(ascending=False)

            plt.figure(figsize=(16, 8))
            sns.set_style("whitegrid")
            plt.xticks(rotation=45)

            sns.barplot(x=grafico.index.str.upper(),
                        y=grafico.values,
                        palette=sns.color_palette("BuGn_r", n_colors=len(grafico.index))).set_title("CIDADES")
            st.pyplot()

        df_download = df[['source', 'target', 'retweet_count', 'url']]

        st.markdown("___")

        st.header('Faça o download do **.csv**: ')
        st.subheader("Esse arquivo está pronto para ser importado pelo Gephi!")
        st.markdown("Não se esqueça de renomear e colocar a extensão `.csv`")
        st.markdown(get_table_download_link(df_download), unsafe_allow_html=True)

        st.header("")
        st.markdown("[![paypal](https://www.paypalobjects.com/pt_BR/BR/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=miguel.s.machado@hotmail.com)")
        st.markdown("Ajuda a manter essa iniciativa **Open Soure** funcionando!")
        st.markdown("Colabore com a comunidade")


if __name__ == '__main__':
    main()