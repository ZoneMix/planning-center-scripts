const axios = require('axios');
const cheerio = require('cheerio');
const qs = require('querystring');

const BASE_WEB_URL = 'https://check-ins.planningcenteronline.com';

const config = {
  jwt: 'JWT',
  personId: 'PERSON_ID', // Person ID for adding trusted contacts to
  householdId: 'HOUSEHOLD_ID', // Household ID of the Person ID
  trustedPersonId: 'TRUSTED_PERSON_ID', // New Trusted Person ID
};

let csrfToken = '';

async function fetchTrustedPeople(personId, jwt) {
  if (!personId || !jwt) {
    throw new Error('Missing required parameters: personId or jwt');
  }

  try {
    const response = await axios.get(`${BASE_WEB_URL}/people/AC${personId}/households`, {
      headers: {
        Cookie: `planning_center_session=${jwt}`,
        Accept: 'text/html',
      },
    });

    const $ = cheerio.load(response.data);
    csrfToken = $('meta[name="csrf-token"]').attr('content') || '';
    const trustedDiv = $('div[data-react-class="people/households/_household_permissions_people"][data-react-props*="trusted"]');
    const props = JSON.parse(trustedDiv.attr('data-react-props') || '{}');

    return props.people || [];
  } catch (error) {
    throw new Error(`Failed to fetch trusted people: ${error.response?.status || error.message}`);
  }
}

async function createTrustedPersonWeb(personId, householdId, jwt) {
  if (!personId || !householdId || !jwt) {
    throw new Error('Missing required parameters: personId, householdId, or jwt');
  }
  if (!csrfToken) {
    throw new Error('CSRF token missing. Run fetchTrustedPeople first.');
  }

  const formData = {
    'person_household_permission[person_account_center_id]': personId,
    'person_household_permission[household_account_center_id]': householdId,
    'person_household_permission[permission]': 'trusted',
  };

  console.log('Form Data:', qs.stringify(formData));

  try {
    const response = await axios.post(
      `${BASE_WEB_URL}/person_household_permissions`,
      qs.stringify(formData),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          Cookie: `planning_center_session=${jwt}`,
          'X-Csrf-Token': csrfToken,
          Accept: 'text/html',
        },
      }
    );
    return response.data;
  } catch (error) {
    const message = error.response?.data
      ? `Failed to create trusted person: ${JSON.stringify(error.response.data)} (Status: ${error.response.status})`
      : `Failed to create trusted person: ${error.message}`;
    throw new Error(message);
  }
}

async function main() {
  try {
    console.log('Fetching current trusted people...');
    const trustedPeople = await fetchTrustedPeople(config.personId, config.jwt);
    console.log('Trusted People:', trustedPeople);

    if (trustedPeople.some(person => person.account_center_id === config.trustedPersonId)) {
      console.log(`Person ${config.trustedPersonId} is already trusted for household ${config.householdId}`);
      return;
    }

    console.log('Creating trusted person (web)...');
    const webResult = await createTrustedPersonWeb(config.trustedPersonId, config.householdId, config.jwt);
    console.log('Created Trusted Person (Web):', webResult);

    console.log('Fetching updated trusted people...');
    const updatedTrustedPeople = await fetchTrustedPeople(config.personId, config.jwt);
    console.log('Updated Trusted People:', updatedTrustedPeople);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
