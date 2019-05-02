const fs = require('fs');


let experiments = fs.readdirSync('results').map(name => {
    return Object.create({
        name,
        iterations: [] 
    })
});

experiments.forEach(ex => {
    let iterations = fs.readdirSync('results/' + ex.name)
    
    iterations.forEach(name => {
        try {
            let kpi = JSON.parse(fs.readFileSync('results/' + ex.name + '/' + name + '/' + fs.readdirSync('results/' + ex.name + '/' + name).
                filter(x => x.endsWith('.kpi'))
            ));
            experiments.iterations.push(kpi);
        } catch (error) {
            console.log(error)
        }
    })
})
