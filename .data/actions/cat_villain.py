{
  "id":"cat-vilain",
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
                  "Soudain, il profite de votre relâchement pour passer à l'attaque!",
                  "Des cornes lui poussent, ses cornées deviennent rouge sang"
                ]
              },
               {
                 "type":"dialogue",
                 "lines":[
                   "Poussant un cri à faire glacer le sang au plus sang-chaud des bourrés après un match, il vous déchique la peau,",
                   "vous retirant ongles et poils, mordant vos tendons, rendant inutilisables vos articulations et méconnaissable votre bras.",
                   "avant de disparaître prestement, comme il était venu, sans un bruit.",
                   "Vous avez eu quelques secondes de bonheur, mais ces choses-là ne durent jamais."
                 ]
               },
              {
                "type":"execution",
                "code":"jeu.equipe.infliger(10)"
              }],
        "vilain":[
          {
            "type":"dialogue",
            "lines":[
              "Mieux vaut passer son chemin,",
              "Plutôt que de se faire aguicher par le malin"
            ]
          }
        ]
      }
    }
  ]
}
