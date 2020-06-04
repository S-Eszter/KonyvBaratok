
const recommended = document.querySelector('#id_recommended');
const wished = document.querySelector('#id_wished');
const loaned = document.querySelector('#id_loaned');
const borrower = document.querySelector('#id_borrower');
const divBorrower = document.querySelector('#div_id_borrower');
const borrowerNonuser = document.querySelector('#id_borrower_nonuser');
const divBorrowerNonuser = document.querySelector('#div_id_borrower_nonuser');
const loanDate = document.querySelector('#id_loan_date');
const divLoanDate = document.querySelector('#div_id_loan_date');
const oldPassword = document.querySelector('#id_old_password');
const newPassword1 = document.querySelector('#id_new_password1');
const newPassword2 = document.querySelector('#id_new_password2');


document.addEventListener('DOMContentLoaded', function () {
    if(wished.checked) {
        recommended.setAttribute('disabled', '');
        loaned.setAttribute('disabled', '');
        borrower.setAttribute('disabled', '');
        divBorrower.setAttribute('disabled', '');
        borrowerNonuser.setAttribute('disabled', '');
        divBorrowerNonuser.setAttribute('disabled', '');
        loanDate.setAttribute('disabled', '');
        divLoanDate.setAttribute('disabled', '');
    } else if(recommended.checked && !loaned.checked) {
        wished.setAttribute('disabled', '');
        borrower.setAttribute('disabled', '');
        divBorrower.setAttribute('disabled', '');
        borrowerNonuser.setAttribute('disabled', '');
        divBorrowerNonuser.setAttribute('disabled', '');
        loanDate.setAttribute('disabled', '');
        divLoanDate.setAttribute('disabled', '');
    } else if(recommended.checked && loaned.checked) {
        wished.setAttribute('disabled', '');
        if(borrowerNonuser.value !== "") {
            borrower.setAttribute('disabled', '');
            divBorrower.setAttribute('disabled', '');          
        } else {
            borrowerNonuser.setAttribute('disabled', '');
            divBorrowerNonuser.setAttribute('disabled', '');
        }
    } else {
        loaned.setAttribute('disabled', '');
        borrower.setAttribute('disabled', '');
        divBorrower.setAttribute('disabled', '');
        borrowerNonuser.setAttribute('disabled', '');
        divBorrowerNonuser.setAttribute('disabled', '');
        loanDate.setAttribute('disabled', '');
        divLoanDate.setAttribute('disabled', '');
    }   
})

document.addEventListener('DOMContentLoaded', function () {
    oldPassword.setAttribute('autocomplete', 'off');
    newPassword1.setAttribute('autocomplete', 'off');
    newPassword2.setAttribute('autocomplete', 'off');
    oldPassword.removeAttribute('autofocus');
})



recommended.addEventListener('change', toggleWishedLoaned);
wished.addEventListener('change', toggleRecommended);
loaned.addEventListener('change', toggleFields);
borrower.addEventListener('change', toggleBorrowerNonuser);
borrowerNonuser.addEventListener('change', toggleBorrower);


function toggleWishedLoaned() {
    if(recommended.checked) {
        loaned.removeAttribute('disabled');
        wished.setAttribute('disabled', '');
        if(loaned.checked) {
            borrower.removeAttribute('disabled');
            divBorrower.removeAttribute('disabled');
            borrowerNonuser.removeAttribute('disabled');
            divBorrowerNonuser.removeAttribute('disabled');
            loanDate.removeAttribute('disabled');
            divLoanDate.removeAttribute('disabled');
        }
    } else {
        wished.removeAttribute('disabled');
        loaned.setAttribute('disabled', '');
        borrower.setAttribute('disabled', '');
        divBorrower.setAttribute('disabled', '');
        borrowerNonuser.setAttribute('disabled', '');
        divBorrowerNonuser.setAttribute('disabled', '');
        loanDate.setAttribute('disabled', '');
        divLoanDate.setAttribute('disabled', '');
    }
}

function toggleRecommended() {
    if(wished.checked) {
      recommended.setAttribute('disabled', '');
    } else {
      recommended.removeAttribute('disabled');
    }
}

function toggleFields() {
    if(loaned.checked) {
        borrower.removeAttribute('disabled');
        divBorrower.removeAttribute('disabled');
        borrowerNonuser.removeAttribute('disabled');
        divBorrowerNonuser.removeAttribute('disabled');
        loanDate.removeAttribute('disabled');
        divLoanDate.removeAttribute('disabled');
    } else {
        borrower.setAttribute('disabled', '');
        divBorrower.setAttribute('disabled', '');
        borrowerNonuser.setAttribute('disabled', '');
        divBorrowerNonuser.setAttribute('disabled', '');
        loanDate.setAttribute('disabled', '');
        divLoanDate.setAttribute('disabled', '');
    }     
}

function toggleBorrowerNonuser() {
    if(borrower.options[borrower.selectedIndex].value !== "") {
        borrowerNonuser.setAttribute('disabled', '');
        divBorrowerNonuser.setAttribute('disabled', ''); 
    } else {
        borrowerNonuser.removeAttribute('disabled');
        divBorrowerNonuser.removeAttribute('disabled'); 
    }  
}

function toggleBorrower() {
    if(borrowerNonuser.value !== "") {
        borrower.setAttribute('disabled', '');
        divBorrower.setAttribute('disabled', ''); 
    } else {
        borrower.removeAttribute('disabled');
        divBorrower.removeAttribute('disabled'); 
    }  
}