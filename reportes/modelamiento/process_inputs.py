import keras
import tensorflow as tf

#diccionarios para num coding
estu_tipodocumento_to_num={"CC":0,"TI":1,"OTHER":2}
zona = {'RURAL': 0,'URBANO': 1}
cole_bilingue_to_num = {"N":0,"S":1,"unknown":-10}
cole_caracter_to_num={"ACADÉMICO":0,"NO APLICA":1, "TÉCNICO":2, "TÉCNICO/ACADÉMICO":3}
cole_genero_to_num={"FEMENINO":0,"MASCULINO":1,"MIXTO":2}
cole_jornada_to_num={"COMPLETA":0,"MAÑANA":1,"NOCHE":2,"SABATINA":3,"TARDE":4,"UNICA":5}
cole_naturaleza_to_num={"NO OFICIAL":0,"OFICIAL":1}
cole_sede_principal_to_num={"S":0,"N":1}
estu_genero_to_num= {"F":0,"M":1,"unknown":-10}
fami_cuartoshogar_to_num={"1 a 2":0,"3 a 4":1,"5":2,"6+":3,"unknown":-10}
fami_educacionm_to_num={"Educación profesional completa":0,
                    "Educación profesional incompleta":1,
                    "Ninguno":2,
                    "No Aplica":2,
                    "No sabe":2,
                    "Postgrado":3,
                    "Primaria completa":4,
                    "Primaria incompleta":5,
                    "Secundaria (Bachillerato) completa":6,
                    "Secundaria (Bachillerato) incompleta":7,
                    "Técnica o tecnológica completa":8,
                    "Técnica o tecnológica incompleta":9,
                    "unknown":-10}
fami_estratovivienda_to_num={ "Estrato 1":1 ,"Estrato 2":2,"Estrato 3":3,"Estrato 4":4,"Estrato 5":5,"Estrato 6":6,"Sin Estrato": -10}
fami_personashogar_to_num = {"1 a 2":0,"3 a 4":1,"5 a 6":2,"7 a 8":3,"9 o más":4,"unknown":-10}
nosi_to_num={"No":0,"Si":1,	"unknown":-10}

# General definitions for the coding
cat_string_feats=["periodo","cole_mcpio_ubicacion"]
cat_num_feats=["estu_tipodocumento","cole_area_ubicacion","cole_bilingue","cole_caracter","cole_genero","cole_jornada","cole_naturaleza","cole_sede_principal","estu_genero","fami_cuartoshogar","fami_educacionmadre","fami_educacionpadre","fami_estratovivienda","fami_personashogar","fami_tieneautomovil","fami_tienecomputador","fami_tieneinternet","fami_tienelavadora"]
possible_targets=["punt_ingles","punt_matematicas","punt_sociales_ciudadanas","punt_c_naturales","punt_lectura_critica","punt_global"]
possible_targets_cat=["desemp_ingles"]
target="punt_global"


def dataframe_to_dataset(dataframe,_target=target):
    dataframe = dataframe.copy()
    labels = dataframe.pop(_target)
    ds = tf.data.Dataset.from_tensor_slices((dict(dataframe), labels))
    ds = ds.shuffle(buffer_size=len(dataframe))
    return ds


def code_features(df):
    df["punt_matematicas"]= df["punt_matematicas"].astype("int64")
    df["punt_ingles"]= df["punt_ingles"].astype("int64")
    df["periodo"]= df["periodo"].astype("string")
    df["estu_tipodocumento"]= df["estu_tipodocumento"].apply(lambda x: estu_tipodocumento_to_num[x])
    df["cole_area_ubicacion"]= df["cole_area_ubicacion"].apply(lambda x: zona[x])
    df["cole_bilingue"]=df["cole_bilingue"].apply(lambda x: cole_bilingue_to_num[x])
    df["cole_caracter"]=df["cole_caracter"].apply(lambda x: cole_caracter_to_num[x])
    df["cole_genero"]=df["cole_genero"].apply(lambda x: cole_genero_to_num[x])
    df["cole_jornada"]=df["cole_jornada"].apply(lambda x: cole_jornada_to_num[x])
    df["cole_mcpio_ubicacion"]=df["cole_mcpio_ubicacion"].astype("category")
    df["cole_naturaleza"]=df["cole_naturaleza"].apply(lambda x: cole_naturaleza_to_num[x])
    df["cole_sede_principal"]=df["cole_sede_principal"].apply(lambda x: cole_sede_principal_to_num[x])
    df["estu_genero"]=df["estu_genero"].apply(lambda x: estu_genero_to_num[x])
    df["fami_cuartoshogar"]=df["fami_cuartoshogar"].apply(lambda x: fami_cuartoshogar_to_num[x])
    df["fami_educacionmadre"]=df["fami_educacionmadre"].apply(lambda x: fami_educacionm_to_num[x])
    df["fami_educacionpadre"]=df["fami_educacionpadre"].apply(lambda x: fami_educacionm_to_num[x])
    df["fami_estratovivienda"]=df["fami_estratovivienda"].apply(lambda x: fami_estratovivienda_to_num[x])
    df["fami_personashogar"]=df["fami_personashogar"].apply(lambda x: fami_personashogar_to_num[x])
    df["fami_tieneautomovil"]=df["fami_tieneautomovil"].apply(lambda x: nosi_to_num[x])
    df["fami_tienecomputador"]=df["fami_tienecomputador"].apply(lambda x: nosi_to_num[x])
    df["fami_tieneinternet"]=df["fami_tieneinternet"].apply(lambda x: nosi_to_num[x])
    df["fami_tienelavadora"]=df["fami_tienelavadora"].apply(lambda x: nosi_to_num[x])
    df["desemp_ingles"]=df["desemp_ingles"].astype("category")

    feats_ordered = cat_num_feats+cat_string_feats
    df = df[feats_ordered+[target]]

    df_ds = dataframe_to_dataset(df)

    batch_size = 32
    df_ds = df_ds.batch(batch_size)

    return df_ds

if __name__ == "__main__":
    code_features()