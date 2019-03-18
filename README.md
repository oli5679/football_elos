# elo_simulator

## Simple Elo simulation of a sports tournament

https://en.wikipedia.org/wiki/Elo_rating_system

## Example - simulate tournament

    import elo
    
    wc_elos = {
        "Uruguay":1954,
        "Russia":1692,
        "Spain":2028,
        "Portugal":1972,
        "France":2007,
        "Denmark":1890,
        "Croatia":1956,
        "Argentina":1918,
        "Brazil":2142,
        "Switzerland":1913,
        "Sweden":1872,
        "Mexico":1843,
        "England":1974,
        "Belgium":1971,
        "Japan":1737,
        "Colombia":1920,
        "Senegal":1782,
        "Germany":1964  
    }

    wc_draw = [
        [
            [
                ['France','Argentina'],
                ['Uruguay','Portugal']
            ],
            [
                ['Brazil','Mexico'],
                ['Belgium','Colombia']
            ]
        ],
        [
            [
                ['Spain','Russia'],
                ['Croatia','Denmark']
            ],

            [
                 ['Sweden','Switzerland'],
                 ['England','Japan']
            ]
        ]
    ]
    
    wc_sim = elo.sim_multiple_tournaments(wc_draw, wc_elos)

## Plot winning chances

    elo.plot_counter(wc_sim, 'World Cup winning prob.')

