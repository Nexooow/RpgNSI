{
  "id":"cat",
  "type":"event-positif",
  "run":[
    {
      "type":"dialogue",
      "lines":[
        "Vous rencontrez un chat sur le chemin"
      ]
    },
    {
      "type":"select",
      "question":"Que voulez-vous faire?",
      "options":[
        {
          "name":"Le caresser",
          "valeur":"pet"
        },
        {
          "name":"Passer votre chemin",
          "valeur":"vilain"
        }
      ],
      "actions":{
        "pet":[{
          "type":"dialogue",
          "lines":[
            "Le chat ronronne et s'enroule autour de votre bras"
          ]
        },
              {
                "type":"dialogue",
                "lines":[
                  "Touché par tant de mignonitude, vous montez au septième ciel"
                ]
              },
              {
                "type":"execution",
                "code":"jeu.equipe.chance+=5"
              }],
        "vilain":[
          {
            "type":"dialogue",
            "lines":[
              "Oh le vilain!",
              "Frapper un chat sans défense!"
            ]
          },
          {
            "type":"execution",
            "code":"jeu.equipe.infliger(5)"
          }
        ]
      }
    }
  ]
}
