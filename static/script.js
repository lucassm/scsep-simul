function checkAuth() {
   const input = document.getElementById('access-code-input').value;
   if (input === CORRECT_CODE) {
      sessionStorage.setItem('is_authenticated', 'true');
      showDashboard();
   } else {
      document.getElementById('auth-error').style.display = 'block';
   }
}

function showDashboard() {
   document.getElementById('auth-modal').style.display = 'none';
   document.getElementById('main-container').style.display = 'block';
   startRefresh();
}

window.onload = function () {
   if (sessionStorage.getItem('is_authenticated') === 'true') showDashboard();
}

function updateCoil(id, value) {
   fetch('update_coil', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id, value: value })
   });
}

function startRefresh() {
   setInterval(() => {
      fetch('get_system_data')
         .then(res => res.json())
         .then(data => {
            // 1. Atualiza a Tabela de Registradores (Normal)
            const regTable = document.getElementById('register-list');
            if (regTable) {
               let html = '';
               data.registers.forEach((val, i) => {
                  html += `<tr>
                            <td style="color:#94a3b8">4000${i + 1}</td>
                            <td class="reg-label">${REGISTER_NAMES[i] || 'Unnamed'}</td>
                            <td class="reg-value">${val}</td>
                        </tr>`;
               });
               regTable.innerHTML = html;
            }

            // 2. SINCRONIZAÇÃO INTELIGENTE DOS COILS (O AJUSTE)
            if (data.coils) {
               data.coils.forEach((val, index) => {
                  const el = document.getElementById('coil_' + index);

                  // SÓ ATUALIZA O BOTÃO SE O USUÁRIO NÃO ESTIVER INTERAGINDO COM ELE
                  // document.activeElement !== el verifica se o botão não está com o foco do clique
                  if (el && document.activeElement !== el) {
                     el.checked = (val === 1 || val === true);
                  }
               });
            }
         })
         .catch(err => console.error("Erro ao atualizar:", err));
   }, 1000);
}
