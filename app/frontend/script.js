let selectedGenes = [];

// 1. Charger les gènes automatiquement
fetch('/genes')
    .then(response => {
        if (!response.ok) throw new Error('Statut HTTP ' + response.status);
        return response.json();
    })
    .then(data => {
        selectedGenes = data.selected_genes;
        const container = document.getElementById('inputs-container');
        container.innerHTML = '';

        // 2. Générer les inputs dynamiquement
        selectedGenes.forEach(gene => {
            container.innerHTML += `
                <div class="form-group">
                    <label>${gene}:</label>
                    <input type="number" step="any" id="${gene}" placeholder="Valeur d'expression...">
                </div>
            `;
        });
    })
    .catch(err => {
        document.getElementById('inputs-container').innerHTML =
            '❌ Impossible de charger les gènes. Le modèle est-il entraîné ? (' + err.message + ')';
    });

// 3. Envoyer POST /predict
function makePrediction() {
    // Validation
    for (const gene of selectedGenes) {
        const val = document.getElementById(gene).value;
        if (val === '' || isNaN(parseFloat(val))) {
            alert('Veuillez renseigner la valeur pour : ' + gene);
            return;
        }
    }

    // Construire le payload (dict plat)
    const data = {};
    selectedGenes.forEach(gene => {
        data[gene] = parseFloat(document.getElementById(gene).value);
    });

    const btn = document.getElementById('predict-btn');
    btn.disabled = true;
    btn.textContent = 'Analyse en cours...';

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) throw new Error('Statut HTTP ' + response.status);
        return response.json();
    })
    .then(result => {
        // 4. Afficher prédiction + confidence
        const resDiv = document.getElementById('result');
        resDiv.className = 'result-box ' + (result.prediction === 'Abnormal' ? 'abnormal' : 'normal');
        resDiv.innerHTML = `
            <strong>Résultat : ${result.prediction}</strong><br>
            Confiance : ${(result.confidence * 100).toFixed(2)}%
        `;
    })
    .catch(err => alert('Erreur lors de la prédiction : ' + err.message))
    .finally(() => {
        btn.disabled = false;
        btn.textContent = '🔍 Prédire';
    });
}
